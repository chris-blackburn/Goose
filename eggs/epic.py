import asyncio
import aiohttp

from .base import Egg, EggException

# TODO: safety in accessing json and error handling, but it's probably good
# enough for now

class EpicEgg(Egg):
    # I found two urls while web scraping epic games store. The sketch
    # looking one gives far less data (in the same format I'd have to
    # request from the graphql endpoint). Since I don't want to deal with
    # pagination from the graphql endpoint, I'm using the sketch one.
    #
    # https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions
    # https://www.epicgames.com/graphql
    endpoint = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
    store = "https://www.epicgames.com/store/product/"

    @property
    def name(self):
        return "Epic Games"

    @staticmethod
    def __is_free(raw):
        """
        So cringe, but with this I can tell if a game is free or not
        """
        try:
            return raw["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["discountSetting"]["discountPercentage"] == 0
        except (KeyError, IndexError, TypeError):
            return False

    @staticmethod
    def __get_thumbnail(raw):
        for key_image in raw["keyImages"]:
            if key_image["type"] == "Thumbnail":
                return key_image["url"]

        return None

    @classmethod
    def filterFree(cls, raw_games):
        args = lambda game: (
            game["id"],
            game["title"],
            game["description"],
            cls.store + game["urlSlug"],
            cls.__get_thumbnail(game)
        )

        construct = lambda game: cls(*args(game))
        freelist = map(construct, filter(cls.__is_free, raw_games))
        return list(freelist)

    @classmethod
    async def fetch(cls):
        async with aiohttp.ClientSession() as session:
            async with session.get(cls.endpoint) as response:
                if response.status != 200:
                    raise EggException("Epic {}".format(response.status))

                body = await response.json()

                try:
                    games = body["data"]["Catalog"]["searchStore"]["elements"]
                except KeyError as e:
                    raise EggException("Epic: {}".format(e))

                return cls.filterFree(games)
