import asyncio
import aiohttp
import time
from .const import Region


class Sc2Api:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._request = RequestHandler(self.client_id, self.client_secret)

    async def get_current_season(self, region, region_id):
        if isinstance(region_id, Region):
            region_id = region_id.value
        url = "https://{}.api.blizzard.com/sc2/ladder/season/{}"
        url = url.format(region, region_id)
        return await self._request.get(url)

    async def get_league_data(self, region, season_id, queue_id,
                              team_type, league_id, locale='en_US'):
        url = "https://{}.api.blizzard.com/data/sc2/league/{}/{}/{}/{}?locale={}"
        url = url.format(region, season_id, queue_id,
                         team_type, league_id, locale)
        return await self._request.get(url)

    async def get_ladder(self, region, ladder_id):
        url = "https://{}.api.blizzard.com/data/sc2/ladder/{}"
        url = url.format(region, ladder_id)
        return await self._request.get(url)

    # async def get_ladder(self, region, region_id, ladder_id):
    #     if isinstance(region_id, Region):
    #         region_id = region_id.value
    #     url = "https://{}.api.blizzard.com/sc2/legacy/ladder/{}/{}"
    #     url = url.format(region, region_id, ladder_id)
    #     return await self._request.get(url)

    async def close(self):
        await self._request.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, type, value, traceback):
        await self.close()


class RequestHandler:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

        self._session = None
        self.token = None
        self.token_expires_at = 0

    async def update_token(self):
        """ Updates token and token_expires_at"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        params = {'grant_type': 'client_credentials'}
        auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
        url = "https://us.battle.net/oauth/token"

        async with self._session.get(url, auth=auth, params=params) as resp:
            data = await resp.json()

        self.token = data['access_token']
        self.token_expires_at = time.time() + data['expires_in']*0.95
        print(self.token)

    async def close(self):
        if self._session:
            await self._session.close()

    async def get(self, url):
        if self.token_expires_at < time.time():
            await self.update_token()
        params = {'access_token': self.token}

        async with self._session.get(url, params=params) as resp:
            result = await resp.json()
            print(resp.url)
        return result
