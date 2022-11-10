import discord
from discord.ext import commands
import json


with open("config.json", "r") as f:
    config = json.load(f)


bot = commands.Bot(command_prefix=".", help_command=None, intents=discord.Intents.all())


@bot.event
async def setup_hook():
    await bot.load_extension("pteraip")
    await bot.tree.sync()


bot.run(config["discord_bot_token"])
