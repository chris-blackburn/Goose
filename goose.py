#!/usr/bin/env python3

import os
import sys
import asyncio

import discord
from discord.ext import commands

import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

DEFAULT_PREFIX = "!"

@commands.command()
async def nest(ctx, minutes: int = 30):
    self = ctx.bot
    self.stop_poll()

    minutes = max(1, minutes)
    self.poll_task = self.loop.create_task(self.poll(ctx.channel, minutes))
    await ctx.send("I will be nesting here now, see you in {} min".format(
        minutes))

@commands.command()
async def honk(ctx):
    self = ctx.bot
    log.info("Checking for golden eggs")
    await ctx.send(await self.do_update())

class Goose(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.none() # TODO: restrict after testing
        intents.messages = True

        super().__init__(command_prefix=DEFAULT_PREFIX,
                guild_subcriptions=False, intents=intents, *args, **kwargs)

        self.add_command(nest)
        self.add_command(honk)

    async def do_update(self):
        return "Sorry, no new golden eggs"

    async def poll(self, channel: discord.TextChannel, minutes=30):
        try:
            while not self.is_closed():
                await asyncio.sleep(max(60, minutes * 60))
                await channel.send(await self.do_update())
        except asyncio.CancelledError:
            pass

    def stop_poll(self):
        task = getattr(self, "poll_task", None)
        if task:
            task.cancel()

if __name__=="__main__":
    token = os.getenv("TOKEN")
    if not token:
        log.error("Please set the TOKEN environment variable")
        sys.exit(1)

    goose = Goose()
    goose.run(token)
