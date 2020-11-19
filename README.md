This is an async wrapper for the sc2 api.

Example of usage:

```py
import asyncio
import sc2api
import logging

logging.basicConfig(level=logging.DEBUG)

MY_CLIENT_ID = ""
MY_CLIENT_SECRET = ""


async def main():
    async with sc2api.Sc2Api(MY_CLIENT_ID, MY_CLIENT_SECRET) as api:
        season_data = await api.ladder.season(sc2api.Region.US)
        season_id = season_data.get('seasonId')

        async def fetch_data_league(region, *args, league):
            return (await api.data.league(region, *args,
                                          league), league, region)

        tasks = [
            (fetch_data_league(region,
                               season_id,
                               sc2api.QueueID.LOTV1V1,
                               sc2api.TeamType.ARRANGED,
                               league=league))
            for league in [sc2api.League.GRANDMASTER, sc2api.League.MASTER]
            for region in [sc2api.Region.US]
        ]

        ladder_ids = set()
        for task in asyncio.as_completed(tasks):
            ladders_data, _, region = await task
            ladder_ids = {
                division['ladder_id']
                for tier in ladders_data.get('tier', {})
                for division in tier.get('division', [])
            }
            tasks = [
                api.data.ladder(region, ladder_id) for ladder_id in ladder_ids
            ]
            data = await asyncio.gather(*tasks)
            for ladder_data in data:
                for player in ladder_data['team']:
                    print(player)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

```
*This script will show all players in the solo grandmaster and master ladders*.