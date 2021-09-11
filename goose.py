#!/usr/bin/env python3

import os
import sys
import asyncio

import discord
from discord.ext import commands

from eggs.epic import EpicEgg

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

DEFAULT_PREFIX = "!"

POLL_INTERVAL = 1

@commands.command()
async def nest(ctx):
    """
    Give goose a channel to update periodically
    """
    self = ctx.bot

    # Replace the old task
    old = self.pollers.get(ctx.channel.id, None)
    if old:
        # TODO: do something more graceful
        old.cancel()

    cb = lambda channel_id: self.pollers.pop(channel_id, None)
    task = self.loop.create_task(self.poll(ctx.channel.id, cb))

    embed = await self.summary()

    self.pollers[ctx.channel.id] = task
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

        self.eggs = [EpicEgg]

        # Probably a better way to do this, but for now, going to keep a
        # dictionary matching channels to polling tasks
        self.pollers = {}

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
        done, pending = await asyncio.wait([egg.fetch() for egg in self.eggs])
        eggs = []
        for fut in done:
            eggs.extend(fut.result())
        return eggs

    async def poll(self, channel_id: int, channel_dead_cb):
        try:
            while not self.is_closed():
                try:
                    await asyncio.sleep(POLL_INTERVAL)
                except asyncio.CancelledError:
                    break

                channel = self.get_channel(channel_id)

                # If the channel doesn't exist, break
                if not channel:
                    break

                results = await self.fetchAll()
                tasks = [self.loop.create_task(channel.send(embed=egg.embed())) \
                        for egg in results]
                asyncio.shield(asyncio.gather(*tasks))
        except asyncio.CancelledError:
            pass
        finally:
            channel_dead_cb(channel_id)

if __name__=="__main__":
    token = os.getenv("TOKEN")
    if not token:
        log.error("Please set the TOKEN environment variable")
        sys.exit(1)

    goose = Goose(log)
    goose.run(token)
