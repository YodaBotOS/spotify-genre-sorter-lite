import os
import json
from urllib.parse import quote, quote_plus

import uvicorn
import fastapi
import config

from fastapi.responses import RedirectResponse as redirect

app = fastapi.FastAPI(title="Spotify Music Genre", version="0", openapi_url=None, docs_url=None, redoc_url=None)

spotify_uri = 'https://accounts.spotify.com/authorize?client_id=%s&response_type=code&redirect_uri=%s&scope=%s'

@app.get("/")
async def root():
    scopes = '%20'.join(config.SPOTIFY_SCOPES)
    redirect_uri = config.SPOTIFY_REDIRECT_URI

    if not redirect_uri.endswith('/callback') and not redirect_uri.endswith('/callback/'):
        return "Error: redirect_uri must end with /callback. Please visit back to your config and update " \
                "the redirect uri. Then restart the program."

    uri = spotify_uri % (config.SPOTIFY_CLIENT_ID, quote_plus(config.SPOTIFY_REDIRECT_URI), scopes)

    if getattr(config, 'SPOTIFY_STATE', None):
        uri += '&state=%s' % quote(config.SPOTIFY_STATE)

    return redirect(uri)

@app.get("/callback")
async def callback(code: str, state: str):
    if state != config.SPOTIFY_STATE:
        return "Error: state does not match."

    js = {'code': code, 'state': state}

    with open('request.json', 'w') as f:
        json.dump(js, f)

    os._exit(0)

def run():
    with open('request.json', 'w') as f:
        json.dump({}, f)

    uvicorn.run(app, **config.WEBSERVER_RUN_CONFIG)

run()