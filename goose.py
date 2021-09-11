#!/usr/bin/env python3

import os
import sys
import asyncio

import discord
from discord.ext import commands

from .eggs.epic import EpicEgg

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

DEFAULT_PREFIX = "!"

DEFAULT_POLL_INTERVAL = 24 * 60 * 60

@commands.command()
async def bonk(ctx):
    await ctx.send("Go to horny jail")

@commands.command()
async def nest(ctx):
    """
    Register a channel with goose to update periodically
    """
    self = ctx.bot

    self.watchers.append(ctx.channel.id)

    embed = await self.summary()
    await ctx.send("Got it, I'll notify you when there are new offers. In the meantime, check out the current offers:")
    await ctx.send(embed=embed)

@commands.command()
async def honk(ctx):
    """
    Check for updates
    """
    self = ctx.bot
    embed = await self.summary()
    await ctx.send(embed=embed)

class Goose(commands.Bot):
    def __init__(self, logger, *args, **kwargs):
        self.log = logger

        intents = discord.Intents.default()
        intents.messages = True

        super().__init__(command_prefix=DEFAULT_PREFIX, intents=intents, *args, **kwargs)

        self.add_command(nest)
        self.add_command(honk)
        self.add_command(bonk)

        self.eggs = [EpicEgg]

        self.loop.create_task(self.broadcast())
        self.watchers = []

    async def summary(self) -> discord.Embed:
        embed = discord.Embed(
                title="Free games",
                color=0xffd700
        )

        all_eggs = await self.fetchAll()

        games = {}
        for egg in all_eggs:
            if egg.name not in games:
                games[egg.name] = []
            games[egg.name].append(egg)

        for source, eggs in games.items():
            embed.add_field(name=source, value="\n".join(
                ["[{}]({})".format(egg.title, egg.url) for egg in eggs]))

        return embed

    async def fetchAll(self):
        tasks = [egg.fetch() for egg in self.eggs]
        results = await asyncio.gather(*tasks)

        eggs = []
        for result in results:
            eggs.extend(result)
        return eggs

    async def broadcast(self):
        poll_interval = int(os.getenv("POLL_INTERVAL",
                default=DEFAULT_POLL_INTERVAL))
        await self.wait_until_ready()
        while not self.is_closed():
            await asyncio.sleep(poll_interval)

            # Get live channels
            self.watchers[:] = filter(self.get_channel, self.watchers)
            channels = [self.get_channel(chid) for chid in self.watchers]

            # TODO: until I have a db, no point in fetching everything
            if not channels:
                continue

            # TODO: Fetch only new, not all
            eggs = await self.fetchAll()

            # send each egg to each channel
            groups = []
            for channel in channels:
                tasks = [self.loop.create_task(channel.send(embed=egg.embed())) \
                        for egg in eggs]
                groups.append(asyncio.gather(*tasks))

            await asyncio.gather(*groups)

if __name__=="__main__":
    token = os.getenv("TOKEN")
    if not token:
        log.error("Please set the TOKEN environment variable")
        sys.exit(1)

    goose = Goose(log)
    goose.run(token)
