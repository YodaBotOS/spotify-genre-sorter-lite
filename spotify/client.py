import asyncio
import datetime
from .http import SpotifyTrackHTTP
from .dataclass import *


def _split(l, amount):
    newl = []
    subl = []

    for i in l:
        subl.append(i)

        if len(subl) >= amount:
            newl.append(subl)
            subl = []

    if subl:
        newl.append(subl)

    return newl


def _exception_catching_callback(task):
    if task.exception():
        task.print_stack()


class Client:
    __slots__ = (
        'client_id',
        'client_secret',
        'session',
        'loop',
        'access_token',
        'refresh_token',
        'expires_in',
        '_requested_on',
        'http',
        '_renew_task',
        '_is_closed',
        '_is_renewing_token',
    )

    def __init__(self, client_id, client_secret, *, session=None, loop=None):
        self.client_id = client_id
        self.client_secret = client_secret

        self.session = session
        self.loop = loop or asyncio.get_event_loop()

        self.access_token = None
        self.refresh_token = None
        self.expires_in = None

        self._requested_on = None

        self.http = SpotifyTrackHTTP(self)

        self._renew_task = None

        self._is_closed = False

        self._is_renewing_token = False

    def is_closed(self) -> bool:
        return self._is_closed

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._is_closed:
            return

        await self.close()

    async def close(self):
        if self._is_closed:
            raise RuntimeError('Client is already closed.')

        if self._renew_task:
            self._renew_task.cancel()

        await self.http.close()

    def wait_while_is_renewing(self):
        while self._is_renewing_token:
            pass

    async def _renew_access_token(self):
        while True:
            if not self.expires_in:
                continue

            if datetime.datetime.utcnow() > self._requested_on + datetime.timedelta(seconds=self.expires_in - 60):  # 60 seconds before it expires, just in case
                self._is_renewing_token = True

                js = await self.http.refresh_access_token(self.refresh_token)

                self.access_token = js['access_token']
                self.expires_in = js['expires_in']

                self.refresh_token = js.get('refresh_token', self.refresh_token)

                self._requested_on = datetime.datetime.utcnow()

                self._is_renewing_token = False

            self._is_renewing_token = False

            await asyncio.sleep(5)

    async def request_access_token(self, code, redirect_uri, *, renew=True) -> dict:
        js = await self.http.fetch_access_token(code, redirect_uri)

        self.access_token = js['access_token']
        self.refresh_token = js['refresh_token']

        self.expires_in = js['expires_in']

        self._requested_on = datetime.datetime.utcnow()

        if renew:
            if self._renew_task:
                self._renew_task.cancel()

            self._renew_task = self.loop.create_task(self._renew_access_token())
            self._renew_task.add_done_callback(_exception_catching_callback)

        return js

    async def get_user_info(self, **kwargs) -> CurrentUser:
        self.wait_while_is_renewing()

        url = 'https://api.spotify.com/v1/me'

        if 'headers' in kwargs:
            kwargs['headers']['Authorization'] = 'Bearer ' + self.access_token
        else:
            kwargs['headers'] = {
                'Authorization': 'Bearer ' + self.access_token
            }

        js = await self.http.request('GET', url, **kwargs)

        return CurrentUser(js)

    async def get_playlist_items(self, playlist_id, *, market='US', fields=None, limit=100, offset=0,
                                 additional_types=None, **kwargs) -> PlaylistItems:
        self.wait_while_is_renewing()

        url = 'https://api.spotify.com/v1/playlists/%s/tracks' % playlist_id

        if 'headers' in kwargs:
            kwargs['headers']['Authorization'] = 'Bearer ' + self.access_token
        else:
            kwargs['headers'] = {
                'Authorization': 'Bearer ' + self.access_token
            }

        params = {
            'market': market,
            'limit': limit,
            'offset': offset
        }

        if fields:
            params['fields'] = fields

        if additional_types:
            params['additional_types'] = additional_types

        if 'params' in kwargs:
            kwargs['params'].update(params)
        else:
            kwargs['params'] = params

        js = await self.http.request('GET', url, **kwargs)

        return PlaylistItems(js)

    async def user_playlists(self, *, limit=50, offset=0, **kwargs) -> CurrentUserPlaylists:
        self.wait_while_is_renewing()

        url = 'https://api.spotify.com/v1/me/playlists'

        if 'headers' in kwargs:
            kwargs['headers']['Authorization'] = 'Bearer ' + self.access_token
        else:
            kwargs['headers'] = {
                'Authorization': 'Bearer ' + self.access_token
            }

        params = {
            'limit': limit,
            'offset': offset
        }

        if 'params' in kwargs:
            kwargs['params'].update(params)
        else:
            kwargs['params'] = params

        js = await self.http.request('GET', url, **kwargs)

        return CurrentUserPlaylists(js)

    async def create_playlist(self, name, *, user_id=None, description=None, public=False, **kwargs) -> CreatedPlaylist:
        self.wait_while_is_renewing()

        if user_id is None:
            user = await self.get_user_info()
            user_id = user.id

        url = 'https://api.spotify.com/v1/users/%s/playlists' % user_id

        if 'headers' in kwargs:
            kwargs['headers']['Authorization'] = 'Bearer ' + self.access_token
        else:
            kwargs['headers'] = {
                'Authorization': 'Bearer ' + self.access_token
            }

        json_dict = {
            'name': name,
            'public': public
        }

        if description:
            json_dict['description'] = description

        if 'json' in kwargs:
            kwargs['json'].update(json_dict)
        else:
            kwargs['json'] = json_dict

        js = await self.http.request('POST', url, **kwargs)

        return CreatedPlaylist(js)

    async def add_playlist_tracks(self, playlist_id, tracks_uri, *, position=None, **kwargs) -> list[AddItemToPlaylist]:
        self.wait_while_is_renewing()

        url = 'https://api.spotify.com/v1/playlists/%s/tracks' % playlist_id

        if 'headers' in kwargs:
            kwargs['headers']['Authorization'] = 'Bearer ' + self.access_token
        else:
            kwargs['headers'] = {
                'Authorization': 'Bearer ' + self.access_token
            }

        tracks = _split(tracks_uri, 100)  # 100 is the limit, so we need to do multiple requests if it is over 100 uris.
        returns = []

        for uris in tracks:
            uri = []

            for u in uris:
                if isinstance(u, Track):
                    uri.append(u.uri)
                else:
                    uri.append(u)

            params = {
                'uris': ','.join(uri),
            }

            if position:
                params['position'] = position

            if 'params' in kwargs:
                kwargs['params'].update(params)
            else:
                kwargs['params'] = params

            js = await self.http.request('POST', url, **kwargs)

            returns.append(AddItemToPlaylist(js))

        return returns

    async def remove_playlist_tracks(self, playlist_id, tracks_uri, **kwargs) -> list[AddItemToPlaylist]:
        self.wait_while_is_renewing()

        url = 'https://api.spotify.com/v1/playlists/%s/tracks' % playlist_id

        if 'headers' in kwargs:
            kwargs['headers']['Authorization'] = 'Bearer ' + self.access_token
        else:
            kwargs['headers'] = {
                'Authorization': 'Bearer ' + self.access_token
            }

        tracks = _split(tracks_uri, 100)  # 100 is the limit, so we need to do multiple requests if it is over 100 uris.
        returns = []

        for uris in tracks:
            uri = []

            for u in uris:
                if isinstance(u, Track):
                    uri.append(u.uri)
                else:
                    uri.append(u)

            # print("uri:", uri)

            json_body = {
                'tracks': [{'uri': u} for u in uri]
            }

            if 'json' in kwargs:
                kwargs['json'].update(json_body)
            else:
                kwargs['json'] = json_body

            js = await self.http.request('DELETE', url, **kwargs)

            returns.append(AddItemToPlaylist(js))

        return returns
