#!/usr/bin/env python3

import os
import sys
import asyncio
import requests

import discord
from discord.ext import commands

from eggs.epic import EpicEgg

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

DEFAULT_PREFIX = "!"

@commands.command()
async def nest(ctx, minutes: int = 30):
    """
    Give goose a channel to update periodically
    """
    self = ctx.bot
    self.stop_poll()

    # Replace the old task
    old = self.pollers.get(ctx.channel.id, None)
    if old:
        # TODO: do something more graceful
        old.cancel()

    minutes = max(30, minutes)
    cb = lambda channel_id: self.pollers.pop(channel_id, None)
    task = self.loop.create_task(self.poll(ctx.channel.id, cb, minutes=minutes))

    self.pollers[ctx.channel.id] = task
    await ctx.send("Got it, I'll send updates here every {} mintues if there are any".format(
        minutes))

@commands.command()
async def honk(ctx):
    """
    Check for updates
    """
    self = ctx.bot
    self.log.info("Checking for golden eggs")
    results = await self.fetchAll()
    await ctx.send(results)

class Goose(commands.Bot):
    def __init__(self, logger, *args, **kwargs):
        self.log = logger

        intents = discord.Intents.default()
        intents.messages = True

        super().__init__(command_prefix=DEFAULT_PREFIX, intents=intents, *args, **kwargs)

        self.add_command(nest)
        self.add_command(honk)

        #self.eggs = [EpicEgg()]
        self.epic = EpicEgg()

        # Probably a better way to do this, but for now, going to keep a
        # dictionary matching channels to polling tasks
        self.pollers = {}

    async def fetchAll(self):
        ## TODO: handle pending
        #done, pending = await asyncio.wait([egg.fetch for egg in self.eggs])
        #return [fut.result() for fut in done]
        return await self.epic.fetch()

    async def poll(self, channel_id: int, channel_dead_cb, minutes: int = 30):
        while not self.is_closed():
            await asyncio.sleep(minutes * 60)

            self.log.debug("Getting channel from id: {}".format(channel_id))
            channel = self.get_channel(channel_id)

            # If the channel doesn't exist, break
            if not channel:
                break

            results = await self.fetchAll()
            asyncio.shield(channel.send(
                "Here's your periodic update: {}".format(results)))

        channel_dead_cb(channel_id)

if __name__=="__main__":
    token = os.getenv("TOKEN")
    if not token:
        log.error("Please set the TOKEN environment variable")
        sys.exit(1)

    goose = Goose(log)
    goose.run(token)
