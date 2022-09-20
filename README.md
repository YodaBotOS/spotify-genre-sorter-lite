# Spotify Genre Sorter Lite
A lightweight and optimized solution for [@YodaBotOS/spotify-genre-sorter](https://github.com/YodaBotOS/spotify-genre-sorter)

This repo uses Python with the Spotify API and OAuth2 to generate a playlist of songs based on the genre and creates a new playlist for that specific genre.

This repo is the same as [@YodaBotOS/spotify-genre-sorter](https://github.com/YodaBotOS/spotify-genre-sorter) but with the following conditions:
- Not locally hosted (AI Genre Classifier uses the [Yoda API](https://api.yodabot.xyz))
- Much more lightweight (optimized by removing more unnecessary code/files and dependencies/requirements)
- Might be a little slower (but optimized to be a little quicker. To make it faster, you can change the mode to `fast` instead of `best` in your config file but it might return false results and sometimes might not work)

# ⚠️ WARNING ⚠️
This project is still a Work In Progress, which means there will be a lot of bugs and unexpected things.

Feel free to experiment with this repo and [report any issues](https://github.com/YodaBotOS/spotify-genre-sorter-lite/issues) you find.

[PRs](https://github.com/YodaBotOS/spotify-genre-sorter-lite/pulls) are always welcomed.

# Credits:
This is taken from [GitHub (@cetinsamet/music-genre-classification)](https://github.com/cetinsamet/music-genre-classification)

All credits go to him for making this amazing repo possible.

# A live demo:
A live demo of this project is available [here](https://playlist.proguy914629.link/grouped). The original version of that playlist is [proguy's playlist](https://playlist.proguy914629.link/all).

# Setup:
The below steps assumed you already have fulfilled the following requirements:
- You have installed Python3.10 or above with pip in your computer. 
- You have [Git](https://git-scm.com/) installed in your computer. (Most OS comes with git built in, especially Linux distros)
- [A Spotify API Client ID and Secret](https://developer.spotify.com)

1. Clone this repository (it might take some time depending on your internet speed).
```shell
git clone https://github.com/YodaBotOS/spotify-genre-sorter-lite
```
2. Install the required dependencies (Note. It is recommended to use a [venv](https://docs.python.org/3/library/venv.html) instead).
```shell
pip install -U -r requirements.txt
```
3. Copy `config.example.py` to the root folder of the repository, named `config.py`.
4. Insert all the values for the essential variables. This includes:
    - `SPOTIFY_PLAYLIST_ID`
    - `SPOTIFY_CLIENT_ID`
    - `SPOTIFY_CLIENT_SECRET`
5. Run the script.
```shell
python3 main.py
```
6. Follow the instructions in your terminal.
