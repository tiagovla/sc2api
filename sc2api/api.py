import asyncio
import aiohttp
import time
from .const import Region
from functools import wraps
from urllib.parse import quote as _uriquote


class RateLimiter():
    """Limits to {limit} number of connections and {rate} requests/second"""

    def __init__(self, rate, limit):
        self.sem = asyncio.Semaphore(limit)
        self.rate = rate

    def __call__(self, fn):
        @wraps(fn)
        async def decorated(*args, **kwargs):
            async with self.sem:
                start = time.monotonic()
                result = await fn(*args, **kwargs)
                diff = time.monotonic() - start
                sleep_for = max(0, 1/self.rate-diff)
                await asyncio.sleep(sleep_for)
                return result
        return decorated


class Sc2Api:

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self._request = RequestHandler(self.client_id, self.client_secret)

        self.profile = ProfileApi(self._request)
        self.ladder = LadderApi(self._request)
        self.account = AccountApi(self._request)
        self.legacy = LegacyApi(self._request)
        self.data = DataApi(self._request)

    async def close(self):
        await self._request.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, type, value, traceback):
        await self.close()


class DataApi:
    def __init__(self, request_handler):
        self._rh = request_handler

    async def league(self, season_id, queue_id, team_type, league_id):
        route = Route('GET', "/data/sc2/league/{season_id}/{queue_id}/{team_type}/{league_id}",
                      season_id=season_id, queue_id=queue_id, team_type=team_type, league_id=league_id)
        return await self._rh.request(route, params={'locale': 'en_US'})

    async def ladder(self, ladder_id):
        route = Route(
            'GET', "/data/sc2/ladder/{ladder_id}", ladder_id=ladder_id)
        return await self._rh.request(route, params={'locale': 'en_US'})


class ProfileApi:
    def __init__(self, request_handler):
        self._rh = request_handler

    async def static(self, region_id):
        route = Route(
            'GET', "/sc2/static/profile/{region_id}", region_id=region_id)
        return await self._rh.request(route, params={'locale': 'en_US'})

    async def metadata(self, region_id, realm_id, profile_id):
        route = Route(
            'GET', "/sc2/metadata/profile/{region_id}/{realm_id}/{profile_id}",
            region_id=region_id, realm_id=realm_id, profile_id=profile_id)
        return await self._rh.request(route, params={'locale': 'en_US'})

    async def profile(self, region_id, realm_id, profile_id):
        route = Route(
            'GET', "/sc2/profile/{region_id}/{realm_id}/{profile_id}",
            region_id=region_id, realm_id=realm_id, profile_id=profile_id)
        return await self._rh.request(route, params={'locale': 'en_US'})

    async def ladder_summary(self, region_id, realm_id, profile_id):
        route = Route('GET',
                      "/sc2/profile/{region_id}/{realm_id}/{profile_id}/ladder/summary",
                      region_id=region_id, realm_id=realm_id,
                      profile_id=profile_id)
        return await self._rh.request(route, params={'locale': 'en_US'})

    async def ladder(self, region_id, realm_id, profile_id, ladder_id):
        route = Route('GET',
                      "/sc2/profile/{region_id}/{realm_id}/{profile_id}/ladder/{ladder_id}",
                      region_id=region_id, realm_id=realm_id,
                      profile_id=profile_id, ladder_id=ladder_id)
        return await self._rh.request(route, params={'locale': 'en_US'})


class LadderApi:
    def __init__(self, request_handler):
        self._rh = request_handler

    async def grand_master(self, region_id):
        route = Route('GET', "/sc2/ladder/grandmaster/{region_id}",
                      region_id=region_id)
        return await self._rh.request(route)

    async def season(self, region_id):
        route = Route('GET', "/sc2/ladder/season/{region_id}",
                      region_id=region_id)
        return await self._rh.request(route)


class AccountApi:
    def __init__(self, request_handler):
        self._rh = request_handler

    async def player(self, account_id):
        route = Route('GET', "/sc2/player/:accountId",
                      account_id=account_id)
        return await self._rh.request(route)


class LegacyApi:
    def __init__(self, request_handler):
        self._rh = request_handler

    async def profile(self, region_id, realm_id, profile_id):
        route = Route('GET',
                      "/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}",
                      region_id=region_id, realm_id=realm_id,
                      profile_id=profile_id)
        return await self._rh.request(route)

    async def ladders(self, region_id, realm_id, profile_id):
        route = Route('GET',
                      "/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}/ladders",
                      region_id=region_id, realm_id=realm_id,
                      profile_id=profile_id)
        return await self._rh.request(route)

    async def match_history(self, region_id, realm_id, profile_id):
        route = Route('GET',
                      "/sc2/legacy/profile/{region_id}/{realm_id}/{profile_id}/matches",
                      region_id=region_id, realm_id=realm_id,
                      profile_id=profile_id)
        return await self._rh.request(route)

    async def ladder(self, region_id, ladder_id):
        route = Route('GET',
                      "/sc2/legacy/ladder/{region_id}/{ladder_id}",
                      region_id=region_id, ladder_id=ladder_id)
        return await self._rh.request(route)

    async def achievements(self, region_id):
        route = Route('GET',
                      "/sc2/legacy/data/achievements/{region_id}",
                      region_id=region_id)
        return await self._rh.request(route)

    async def rewards(self, region_id):
        route = Route('GET',
                      "/sc2/legacy/data/rewards/{region_id}",
                      region_id=region_id)
        return await self._rh.request(route)


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

    @ RateLimiter(100, 100)
    async def get(self, url):
        if self.token_expires_at < time.time():
            await self.update_token()
        params = {'access_token': self.token}

        async with self._session.get(url, params=params) as resp:
            result = await resp.json()
            print(resp.url)
        return result

    async def request(self, route, **kwargs):
        if self.token_expires_at < time.time():
            await self.update_token()
        method = route.method
        url = route.url
        kwargs['params'] = {'access_token': self.token,
                            **kwargs.get('params', {})}
        async with self._session.request(method, url, **kwargs) as r:
            try:
                data = await r.json()
            except aiohttp.client_exceptions.ContentTypeError:
                data = await r.text()
            print(r.url)
        return data


class Route:
    BASE = "https://us.api.blizzard.com"

    def __init__(self, method, path, **params):
        self.path = path
        self.method = method
        url = self.BASE + self.path
        if params:
            self.url = url.format(
                **{k: _uriquote(v) if isinstance(v, str) else v
                   for k, v in params.items()})
        else:
            self.url = url
