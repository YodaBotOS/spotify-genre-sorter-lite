# ⚠️ WARNING ⚠️
# DO NOT REMOVE/RENAME ANY VARIABLES ALREADY PREPARED HERE AS THEY ARE CRITICAL AND CRUCIAL TO THE
# SCRIPT UNLESS YOU KNOW WHAT YOU ARE DOING.
# PLEASE JUST MODIFY THE VARIABLE VALUES AND NOT REMOVE/RENAME THEM.

SPOTIFY_PLAYLIST_ID = ''

# Spotify OAuth2 Stuff
SPOTIFY_CLIENT_ID = ''
SPOTIFY_CLIENT_SECRET = ''

SPOTIFY_SCOPES = [
    #'playlist-read-public', # A invaild Spotify OAuth2 Scope
    'playlist-read-private',

    'playlist-modify-public',
    'playlist-modify-private',

    'user-read-private',
    'user-read-email',
]

# make sure to add the redirect URI you passed into your client's valid Redirect URIs with the host/domain.
SPOTIFY_REDIRECT_URI = '/callback'
SPOTIFY_STATE = ''

# Webserver stuff
# Please refer to https://uvicorn.org/settings/ for more info on what to set here.
WEBSERVER_RUN_CONFIG = {
    'host': '127.0.0.1',
    'port': 8080
}

# Genre stuff
GENRES_IGNORED = [
    # This ignores a specific genre, making them not be added to the playlist and not creating that specific playlist.
    # The available genres (by default) are:
    # 'blues',
    # 'classical',
    # 'country',
    # 'disco',
    # 'hiphop',
    # 'jazz',
    # 'metal',
    # 'pop',
    # 'reggae',
    # 'rock',
    # Feel free to uncomment the genres listed above to ignore them.
]

GENRE_PLAYLIST_NAME = {
    # This represents a dict of `genre: name`.
    # This will be used to set a specific playlist name for each genre playlist.
}
# This is the playlist name for fallbacks of GENRE_PLAYLIST_NAME if the genre isn't present there.
# The "{}" is to be replaced with the actual genre name, in this case it will be something like "Pop Genre Playlist".
# The "{}" just calls `.format(genre)` on the string. It is optional to have it present on the string.
# Any `.format` syntax is applicable here e.g {0}, {!s}, etc.
GENRE_DEFAULT_PLAYLIST_NAME = '{} Genre Playlist'

# HINT: Description supports `None` or an empty string as a value to represent no description to the playlist.
GENRE_PLAYLIST_DESCRIPTION = {
    # This represents a dict of `genre: description`.
    # This will be used to set a specific description for each genre playlist.
}
# This is the description for fallbacks of GENRE_PLAYLIST_DESCRIPTION if the genre isn't present there.
# The "{}" is supported here. For more info, look at the comment for GENRE_PLAYLIST_NAME.
GENRE_DEFAULT_PLAYLIST_DESCRIPTION = ''

GENRE_PLAYLIST_PUBLIC = {
    # This sets the publicity of the genre playlists.
    # This represents a dict of `genre: publicity`, `publicity` being a boolean of `True` or `False`.
    # This will be used to set a specific publicity for each genre playlist.
}
# This is the description for fallbacks of GENRE_PLAYLIST_PUBLIC if the genre isn't present there.
GENRE_DEFAULT_PLAYLIST_PUBLIC = True

# Configurations
MODE = "best"  # fast, best
