import aiohttp

from .base import Egg, EggSource, EggException

@Egg.source(EggSource.EPIC)
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

    @staticmethod
    def _is_free(raw):
        try:
            return raw["promotions"]["promotionalOffers"][0]["promotionalOffers"][0]["discountSetting"]["discountPercentage"] == 0
        except (KeyError, IndexError, TypeError):
            return False

    @staticmethod
    def _get_thumbnail(raw):
        for key_image in raw["keyImages"]:
            if key_image["type"] == "Thumbnail":
                return key_image["url"]

        return None

    @staticmethod
    def _get_page_url(raw):
        # If there is an offer mappings array, then we need to find the element
        # with the productHome page type and use that url, otherwise, it has to
        # be the urlslug
        for mapping in raw["offerMappings"]:
            if mapping["pageType"] == "productHome":
                return mapping["pageSlug"]

        return raw["urlSlug"]

    @classmethod
    def _filter_free(cls, raw_games):
        args = lambda game: (
            game["id"],
            game["title"],
            game["description"],
            cls.store + cls._get_page_url(game),
            cls._get_thumbnail(game)
        )

        construct = lambda game: cls(*args(game))
        freelist = map(construct, filter(cls._is_free, raw_games))
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

                return cls._filter_free(games)
