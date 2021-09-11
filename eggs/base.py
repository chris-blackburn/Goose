import asyncio
from discord import Embed

class EggException(Exception):
    pass

class Egg:
    """
    Eggs are games
    """
    def __init__(self, gid, title, description, url, thumbnail):
        self.id = gid
        self.title = title
        self.description = description
        self.url = url
        self.thumbnail = thumbnail

    def __str__(self):
        return "title={},url={}".format(self.title, self.url)

    @property
    def name(self):
        return self.__class__.__name__

    def embed(self) -> Embed:
        embed = Embed(
                title="{} is now free on {}".format(self.title, self.name),
                description=self.description,
                url=self.url,
                color=0xffd700
        )
        embed.set_image(url=self.thumbnail)
        embed.set_footer(text="Free games from {}".format(self.name))

        return embed

    @classmethod
    async def fetch(cls):
        """
        Factory for eggs - should reach out to the egg's store and return a list
        of this egg's intances
        """
        raise NotImplemented
