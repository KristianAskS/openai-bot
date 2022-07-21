import os
import random

import nextcord
import openai as oa
from dotenv import load_dotenv
from nextcord import Interaction
from nextcord.ext import commands

from petit import get_petit_url
from videofetcher import DailyLimitReached, get_vids

API_KEYS = []

intents = nextcord.Intents.default()

intents.members = True

client = commands.Bot(command_prefix="?", intents=intents)


cached_videos = []


@client.command()
async def openai(ctx: Interaction, *, args):
    if not args:
        return

    async with ctx.channel.typing():
        response = oa.Completion.create(
            model="text-davinci-002",
            prompt=" ".join(args),
            temperature=0.7,
            max_tokens=380,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        try:
            await ctx.reply(response["choices"][0]["text"])
        except Exception:
            await ctx.reply("Error")


@client.command()
async def petittube(ctx: Interaction):
    await ctx.reply(get_petit_url())


@client.command()
async def randomvid(ctx: Interaction):
    """Fetches a video from the deepest depths of YouTube"""
    async with ctx.channel.typing():
        for key in API_KEYS:
            try:
                # check if there's cached videos
                if cached_videos:
                    random.shuffle(cached_videos)
                    video = cached_videos.pop()

                    link = f"https://www.youtube.com/watch?v={video['id']}"
                    await ctx.reply(link)
                    return

                vids = get_vids(key)

                random.shuffle(vids)
                random_vid = vids.pop()

                cached_videos.extend(vids)

                link = f"https://www.youtube.com/watch?v={random_vid['id']}"

                await ctx.reply(link)
                return

            except DailyLimitReached:
                continue

            except Exception:
                await ctx.reply("Error")
                return


@client.event
async def on_ready():
    print("bot ready")


if __name__ == "__main__":
    load_dotenv()
    oa.api_key = os.getenv("OPENAI_API_KEY")
    client.run(os.getenv("DISCORD_TOKEN"))
