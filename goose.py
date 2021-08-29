#!/usr/bin/env python3

import os
import sys
import asyncio
import requests

import discord
from discord.ext import commands

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

DEFAULT_PREFIX = "!"

@commands.command()
async def nest(ctx, minutes: int = 30):
    self = ctx.bot
    self.stop_poll()

    minutes = max(1, minutes)
    self.poll_task = self.loop.create_task(self.poll(ctx.channel.id, minutes))
    await ctx.send("I will be nesting here now, see you in {} min".format(
        minutes))

@commands.command()
async def honk(ctx):
    self = ctx.bot
    self.log.info("Checking for golden eggs")
    await ctx.send(await self.do_update())

class Goose(commands.Bot):
    def __init__(self, logger, *args, **kwargs):
        intents = discord.Intents.default()
        intents.messages = True

        super().__init__(command_prefix=DEFAULT_PREFIX, intents=intents, *args, **kwargs)

        self.add_command(nest)
        self.add_command(honk)

        self.log = logger

    async def do_update(self):
        r = requests.get("https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions")
        if r.status_code != 200:
            self.log.info("Received {} from epic games".format(r.status_code))
            return "Sorry, no new golden eggs"

        body = r.json()

        def weekly(game):
            if game["promotions"] and \
                    len(game["promotions"]["promotionalOffers"]):
                return True

            return False

        free_games = filter(weekly,
                body["data"]["Catalog"]["searchStore"]["elements"])
        titles = map(lambda game : game["title"], free_games)
        return "Awwww yeah, sweet golden eggs: {}".format(list(titles))

    async def poll(self, channel_id: int, minutes: int = 30):
        try:
            while not self.is_closed():
                await asyncio.sleep(max(60, minutes * 60))
                self.log.debug("Getting channel from id: {}".format(channel_id))
                channel = self.get_channel(channel_id)
                if not channel:
                    self.poll_task = None
                    break
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

    goose = Goose(log)
    goose.run(token)
