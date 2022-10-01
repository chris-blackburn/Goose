import os
import asyncio

import discord
from discord.ext import commands

from .eggs import Egg
from . import DEFAULT_PREFIX, DEFAULT_POLL_INTERVAL

import logging
logging.basicConfig()
logger = logging.getLogger("goose")
logger.setLevel(logging.DEBUG)

"""
class Watcher:

    guild
    channel

    broadcasted = {}
"""

@commands.command()
async def nest(ctx):
    """
    Register a channel with goose to update periodically
    """
    self = ctx.bot

    self.watchers.append(ctx.channel.id)

    embed = await self.summary()
    await ctx.send("I'll notify you when there are new offers. In the meantime, check out the current offers:")
    await ctx.send(embed=embed)

@commands.command()
async def honk(ctx):
    """
    Check for updates
    """
    self = ctx.bot
    embed = await self.summary()
    await ctx.send(embed=embed)

@commands.command()
async def broadcast(ctx):
    """
    force a broadcast
    """
    self = ctx.bot
    await self._broadcast()

class Goose(commands.Bot):
    def __init__(self, *args, **kwargs):

        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True

        super().__init__(command_prefix=DEFAULT_PREFIX, intents=intents, *args, **kwargs)

        self.add_command(nest)
        self.add_command(honk)
        self.add_command(broadcast)

        # TODO per guild (channel) record of what has already been displayed
        self.broadcasted = {}
        self.watchers = []

    async def setup_hook(self):
        asyncio.create_task(self.broadcast_loop())

    async def summary(self) -> discord.Embed:
        embed = discord.Embed(
                title="Free games",
                color=0xffd700
        )

        games = {}
        for egg in await Egg.fetchall():
            if egg.name not in games:
                games[egg.name] = []
            games[egg.name].append(egg)

        for source, eggs in games.items():
            embed.add_field(name=source, value="\n".join(
                ["[{}]({})".format(egg.title, egg.url) for egg in eggs]))

        return embed

    async def _broadcast(self):
        # Get live channels
        self.watchers[:] = filter(self.get_channel, self.watchers)
        channels = [self.get_channel(chid) for chid in self.watchers]

        if not channels:
            return

        eggs = []
        for egg in await Egg.fetchall():
            if egg.id not in self.broadcasted.keys():
                eggs.append(egg)
            self.broadcasted[egg.id] = egg

        # send each egg to each channel
        groups = []
        for channel in channels:
            tasks = [channel.send(embed=egg.embed()) for egg in eggs]
            groups.append(asyncio.gather(*tasks))

        await asyncio.gather(*groups)

    async def broadcast_loop(self):
        poll_interval = int(os.getenv("POLL_INTERVAL",
                default=DEFAULT_POLL_INTERVAL))
        await self.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(poll_interval)
            await self._broadcast()
