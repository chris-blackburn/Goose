import asyncio
import enum
from dataclasses import dataclass, field
from typing import Dict

from discord import Embed

class EggException(Exception):
    pass

class EggSource(enum.Enum):
    EPIC = "Epic Games"

Egg = None

@dataclass
class Egg:
    """
    Eggs are games
    """

    id: str
    title: str
    description: str
    url: str
    thumbnail: str

    __eggs = {}

    def embed(self) -> Embed:
        name = self.name
        embed = Embed(
                title="{} is now free on {}".format(self.title, name),
                description=self.description,
                url=self.url,
                color=0xffd700
        )
        embed.set_image(url=self.thumbnail)
        embed.set_footer(text="Free games from {}".format(name))

        return embed

    @classmethod
    def source(cls, name: EggSource):
        def decorator(subcls):
            setattr(subcls, "name", name.value)
            cls.__eggs[name] = subcls
            return subcls
        return decorator

    @classmethod
    async def fetch(cls):
        """
        Factory for eggs - should reach out to the egg's store and return a
        list of this egg's intances
        """
        raise NotImplementedError

    @classmethod
    async def fetchall(cls):
        """
        Factory for eggs - should reach out to the egg's store and return a
        list of this egg's intances
        """

        tasks = [egg.fetch() for egg in cls.__eggs.values()]
        results = await asyncio.gather(*tasks)

        eggs = []
        for result in results:
            eggs.extend(result)

        return eggs

from .epic import EpicEgg
