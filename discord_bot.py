import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.command(name="here")
async def set_target_channel(ctx: discord.ext.commands.context.Context):
    target_channel_id = ctx.channel.id
    print(ctx)
    print(target_channel_id)
    await ctx.send(f'Target channel set to {ctx.channel.name}')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(DISCORD_TOKEN)
