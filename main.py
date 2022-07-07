import os

import nextcord
import openai as oa
from dotenv import load_dotenv
from nextcord import Interaction
from nextcord.ext import commands

intents = nextcord.Intents.default()

intents.members = True

client = commands.Bot(command_prefix="?", intents=intents)


@client.command()
async def openai(ctx: Interaction, *args):
    response = oa.Completion.create(
        model="text-davinci-002",
        prompt=" ".join(args),
        temperature=0.7,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )

    try:
        await ctx.reply(response["choices"][0]["text"])
    except Exception:
        await ctx.reply("Error")


@client.event
async def on_ready():
    print("bot ready")


if __name__ == "__main__":
    load_dotenv()
    oa.api_key = os.getenv("OPENAI_API_KEY")
    client.run(os.getenv("DISCORD_TOKEN"))
