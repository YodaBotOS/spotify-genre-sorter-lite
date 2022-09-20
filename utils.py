import asyncio

import aiohttp

import config
import spotify

from core.api import GenrePrediction as GPred


def check_imports() -> tuple[bool, ImportError | None]:
    try:
        import aiohttp
        import fastapi
        import uvicorn
    except ImportError as e:
        return False, e
    else:
        return True, None


async def get_available(client: spotify.Client) -> tuple[dict[str, dict], dict[str, dict[spotify.Track, list[int]]]]:
    tracks_available = {
        'playlist-track': {},
        # 'track-playlist': [],
    }

    playlists = []
    offset = 0

    user = await client.get_user_info()

    while True:
        response = await client.user_playlists(limit=50, offset=offset)

        if not response.items:
            break

        playlists += response.items

        offset += response.limit

    _available_playlists = [x for x in playlists if x['owner']['id'] == user.id and x['name'] in [
        config.GENRE_PLAYLIST_NAME.get(genre, config.GENRE_DEFAULT_PLAYLIST_NAME.format(genre.title())) for genre in
        ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']
    ]]

    available_playlists = {}

    for i in _available_playlists:
        for genre in ['blues', 'classical', 'country', 'disco', 'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']:
            if config.GENRE_PLAYLIST_NAME.get(genre,
                                              config.GENRE_DEFAULT_PLAYLIST_NAME.format(genre.title())) == i['name']:
                available_playlists[genre] = i

    for genre, playlist in available_playlists.items():
        offset = 0

        tracks = []

        playlist_id = playlist['id']

        while True:
            response_tracks = await client.get_playlist_items(playlist_id, offset=offset, limit=100)

            if not response_tracks.items:
                break

            tracks += [x['track'] for x in response_tracks.items]

            offset += response.limit

        tracks_available['playlist-track'][playlist_id] = tracks

    return available_playlists, tracks_available


async def run_genre_classification(track: spotify.Track, mode: str = None) -> dict[str, float]:  # func = get_genre
    mode = mode or config.MODE

    url = track.preview_url

    if mode not in ["fast", "best"]:
        raise ValueError(f"Invalid mode: {mode}")

    async with aiohttp.ClientSession() as session:
        gpred = GPred(session=session, api_version='latest')

        genres, start, end, elapsed = await gpred(url, mode=mode)  # type: ignore

    return genres


def handle_removed_tracks(tracks: list[spotify.Track], tracks_before: list[spotify.Track]) -> list[spotify.Track]:
    # returns the removed tracks
    removed_tracks = []

    for track in tracks_before:
        if track in tracks_before and track not in tracks:
            removed_tracks.append(track)

    return removed_tracks


async def handle_with_semaphore(sem, client, track, genre_tracks):
    try:
        genres = await run_genre_classification(track)
    except Exception as e:
        raise e

    async with sem:
        for genre, confidence in genres.items():
            if not genre or not confidence or genre.lower() in [x.lower() for x in config.GENRES_IGNORED]:
                continue

            if genre not in genre_tracks:
                genre_tracks[genre] = []

            genre_tracks[genre].append({
                'track': track,
                'confidence': confidence,
            })

            available_playlists, tracks_available = await get_available(client)

            if genre not in available_playlists:
                playlist_created = False
            else:
                playlist_created = True
                playlist_id = available_playlists[genre]['id']

            offset = 0
            tracks = []

            if playlist_created is True:
                while True:
                    response_tracks = await client.get_playlist_items(playlist_id, offset=offset, limit=100)  # type: ignore

                    if not response_tracks.items:
                        break

                    tracks += [x['track'] for x in response_tracks.items]

                    offset += response_tracks.limit

            tracks_to_add = [track if track not in tracks else None]

            if not tracks_to_add:
                continue

            if playlist_created is False:
                description = config.GENRE_DEFAULT_PLAYLIST_DESCRIPTION or ''
                playlist = await client.create_playlist(
                    config.GENRE_PLAYLIST_NAME.get(genre, config.GENRE_DEFAULT_PLAYLIST_NAME.format(genre.title())),
                    description=config.GENRE_PLAYLIST_DESCRIPTION.get(
                        genre, description.format(genre.title())
                    ) or None,
                    public=config.GENRE_PLAYLIST_PUBLIC.get(genre, config.GENRE_DEFAULT_PLAYLIST_PUBLIC),
                )
                playlist_id = playlist.id

            await client.add_playlist_tracks(playlist_id, tracks_to_add)

            print(f"[LOGS] Added tracks {track.name} to {playlist_id} ({genre}) with confidence of {confidence}")

            await asyncio.sleep(.75)  # avoiding rate-limits cause im too lazy to handle them


async def check_new_tracks(client: spotify.Client, *, tracks_before: list[spotify.Track] = None):
    tracks_before = tracks_before or []

    sem = asyncio.Semaphore(1)

    while True:
        offset = 0

        tracks = []

        while True:
            response_tracks = await client.get_playlist_items(config.SPOTIFY_PLAYLIST_ID, offset=offset, limit=100)

            if not response_tracks.items:
                break

            tracks += [x['track'] for x in response_tracks.items]

            offset += response_tracks.limit

        original_tracks = tracks.copy()

        available_playlists, tracks_available = await get_available(client)

        for playlist, playlist_tracks in tracks_available['playlist-track'].items():
            to_be_removed = []

            for playlist_track in playlist_tracks:
                if playlist_track not in tracks:
                    to_be_removed.append(playlist_track)

            if not to_be_removed:
                continue

            print(f"[LOGS] Removing tracks from {playlist} playlist: {to_be_removed}")
            await client.remove_playlist_tracks(playlist, to_be_removed)

        for playlist, playlist_tracks in tracks_available['playlist-track'].items():
            for track in tracks:
                if track in playlist_tracks:
                    tracks.remove(track)

        genre_tracks = {}

        for track in tracks:
            if track in tracks_before:
                continue

            if not track.preview_url or not isinstance(track.preview_url, str):
                continue

            asyncio.create_task(handle_with_semaphore(sem, client, track, genre_tracks))

        tracks_before = original_tracks

        await asyncio.sleep(5)
