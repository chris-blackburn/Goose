import asyncio
import aiohttp

class EggException(Exception):
    pass

class Egg:
    @property
    def name(self):
        return self.__class__.__name__
