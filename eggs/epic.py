import asyncio
import aiohttp

from .base import Egg, EggException

class EpicGame:
    BASE_URL = "https://www.epicgames.com/store/en-US/p/"

    def __init__(self, title, urlSlug):
        self.title = title
        self.url = self.BASE_URL + urlSlug

    def __str__(self):
        return "title={},url={}".format(self.title, self.url)

    @staticmethod
    def __is_free(raw):
        """
        So cringe, but with this I can tell if a game is free or not
        """
        try:
            return raw["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["discountSetting"]["discountPercentage"] == 0
        except (KeyError, IndexError, TypeError):
            return False

    @classmethod
    def filterFree(cls, raw_games):
        freelist = map(lambda game: cls(game["title"], game["urlSlug"]),
                filter(cls.__is_free, raw_games))
        return list(freelist)

class EpicEgg(Egg):
    def __init__(self):
        # I found two urls while web scraping epic games store. The sketch
        # looking one gives far less data (in the same format I'd have to
        # request from the graphql endpoint). Since I don't want to deal with
        # pagination from the graphql endpoint, I'm using the sketch one.
        #
        # https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions
        # https://www.epicgames.com/graphql
        self.endpoint = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"

    async def fetch(self, only_new=True):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.endpoint) as response:
                if response.status != 200:
                    raise EggException("Epic {}".format(response.status))

                body = await response.json()

                try:
                    games = body["data"]["Catalog"]["searchStore"]["elements"]
                except KeyError as e:
                    raise EggException("Epic: {}".format(e))

                return EpicGame.filterFree(games)
