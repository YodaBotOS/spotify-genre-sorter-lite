import aiohttp
import asyncio
import logging
from .utils import json_or_text
from .error import *

__log__ = logging.getLogger(__name__)

class SpotifyTrackHTTP:
    __slots__ = (
        '_session',
        '_loop',
        '_client',
        '_session_created_locally',
        '_lock',
        '_tries',
    )

    def __init__(self, client):
        self._client = client

        self._session_created_locally: bool = False

        self._session: aiohttp.ClientSession = client.session

        self._loop: asyncio.AbstractEventLoop = client.loop or asyncio.get_event_loop()

        #if self._session is None:
            #self._session: aiohttp.ClientSession = self._loop.run_until_complete(self._generate_session())

        self._lock: asyncio.Lock = asyncio.Lock()

        self._tries = 5

    async def _generate_session(self) -> aiohttp.ClientSession:
        self._session = aiohttp.ClientSession(loop=self._loop)
        self._client.session = self._session

        self._session_created_locally = True

        return self._session

    async def close(self):
        if self._session_created_locally:
            await self._session.close()

    async def request(self, method, url, **kwargs) -> dict:
        # while self._client._is_renewing_token:
        #     pass

        if self._session is None:
            await self._generate_session()

        tries = self._tries

        async with self._lock:
            while tries > 0:
                tries -= 1

                async with self._session.request(method, url, **kwargs) as response:
                    data = await json_or_text(response)
                    data = data or {}

                    if 200 <= response.status < 300:
                        return data
                    elif response.status == 429:
                        if not response.headers.get('Via') or isinstance(data, str):
                            # Most likely getting banned.
                            raise SpotifyTrackHTTPException(response, data)

                        # Handle rate limit

                        fmt = 'We are being rate limited. Retrying in %.2f seconds.'

                        retry_after: float = float(response.headers.get('Retry-After'))

                        __log__.warning(fmt, retry_after)

                        await asyncio.sleep(retry_after)

                        __log__.debug('Done sleeping for the rate limit. Retrying...')
                    elif response.status in {500, 502, 504}:
                        # we've received a 500, 502, or 504, unconditional retry
                        await asyncio.sleep(1 + tries * 2)

            raise SpotifyTrackHTTPException(response, data)

    # Endpoints:
    async def fetch_access_token(self, code, redirect_uri):
        url = 'https://accounts.spotify.com/api/token'

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': self._client.client_id,
            'client_secret': self._client.client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        js = await self.request('POST', url, data=data, headers=headers)

        return js

    async def refresh_access_token(self, refresh_token):
        url = 'https://accounts.spotify.com/api/token'

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': self._client.client_id,
            'client_secret': self._client.client_secret
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        js = await self.request('POST', url, data=data, headers=headers)

        return js