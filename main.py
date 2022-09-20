import os
import sys
import json
import asyncio
import subprocess

import config
import spotify
from utils import *

print("[+] Please wait. Checking required imports...")

check = check_imports()

if check[0] is False:
    raise ImportError(f'Library {check[1].name} is not installed. Please install all the required libraries from '
                      f'"requirements.txt" file by doing "pip install -r requirements.txt" or similar.') from None

print("[+] Starting...")

# print("[+] Checking for updates...")
#
# process = subprocess.Popen(["git", "pull"])
# stdout, stderr = process.communicate()
#
# stdout = stdout or b''
# stderr = stderr or b''
#
# if stdout.decode('utf-8') == "Already up to date." or stderr.decode('utf-8') == "Already up to date.":
#     pass
# else:
#     print("[+] Update successful!")
#     print("[+] Restarting... Please start the program again.")
#
#     os._exit(0)

print("[+] Starting webserver...")

print("-" * 25)
print("Make sure to sign-in using the user that you want to use to add the playlists.")
print("Note that this software only supports public playlists. This software does not work for private playlists nor "
      "liked songs.")
print("Also, make sure to add the redirect URI you passed in your config to your client's valid Redirect URIs.")

status_code = os.system(sys.executable + " " + os.path.dirname(os.path.abspath(__file__)) + "/webserver.py")

if status_code != 0:  # Exited abnormally
    print("[-] Webserver exited abnormally. Please try again. If this is a bug, please submit an issue on GitHub, "
          "https://github.com/OpenRobot/spotify-music-genre")
    os._exit(1)

print("[+] Spotify WebServer has been stopped")

if not os.path.exists("request.json"):
    print("[-] No request.json file found. The webserver failed to generate a request.json file. "
          "Please run the program again.")
    os._exit(1)

try:
    with open("request.json", "r") as f:
        js_callback = json.load(f)
except FileNotFoundError:
    print("[-] No request.json file found. The webserver failed to generate a request.json file. "
          "Please run the program again.")
    os._exit(1)

code = js_callback["code"]
state = js_callback["state"]

with open("request.json", "w") as f:
    json.dump({}, f)

print("[+] Request.json has been cleared")

print("[+] Requesting for a Access Token from Spotify")


async def coro():
    async with spotify.Client(config.SPOTIFY_CLIENT_ID, config.SPOTIFY_CLIENT_SECRET) as client:
        # try:
        await client.request_access_token(code, config.SPOTIFY_REDIRECT_URI, renew=True)

        print(f"[+] Getting User information...")

        user = await client.get_user_info()

        confirm_user = input(f"Are you sure that you want to add the Genre playlists on {user.display_name} | "
                             f"{user.external_urls['spotify']} [Y/n] ")

        while True:
            if confirm_user.lower() in ['', 'y', 'yes']:
                break
            elif confirm_user.lower() in ['n', 'no']:
                print("[+] Exiting...")
                os._exit(0)
            else:
                confirm_user = input("Please enter 'Y' or 'N' as your answer: ")

        print("[+] Logged in as User: {} | {}".format(user.display_name, user.external_urls['spotify']))

        print("[+] Running Music Genre Classification")

        try:
            await check_new_tracks(client)
        except Exception as e:
            raise e


def exception_catching_callback(task):
    if task.exception():
        task.print_stack()


try:
    task = asyncio.run(coro())
    task.add_done_callback(exception_catching_callback)
except KeyboardInterrupt:
    print("[-] Exiting...")

    try:
        remove_tmp()
    except:
        pass

    os._exit(0)
