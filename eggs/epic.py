import asyncio
import aiohttp

class EggException(Exception):
    pass

class Egg:
    pass

class EpicEgg(Egg):
    def __init__(self):
        self.endpoint = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    async def processResponse(self, response):
        if response.status != 200:
            self.log.info("Received {} from epic games".format(response.status))
            raise EggException("Epic {}".format(response.status))

        body = await response.json()

        # TODO: grab the links instead and maybe clean up this garbage
        weekly = lambda game: (game["promotions"] and \
                len(game["promotions"]["promotionalOffers"]))

        free_games = filter(weekly,
                body["data"]["Catalog"]["searchStore"]["elements"])
        titles = map(lambda game : game["title"], free_games)
        return list(titles)

    async def _fetch(self, session):
        async with session.get(self.endpoint) as response:
            return await self.processResponse(response)

    async def fetch(self):
        async with aiohttp.ClientSession() as session:
            return await self._fetch(session)
