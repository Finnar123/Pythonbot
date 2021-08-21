import io
import discord
#import random
from discord import activity, Client
from discord import channel
from discord.ext import commands, tasks
#from discord.ext.commands import cooldown, BucketType, MissingPermissions
#from PIL import Image, ImageFont, ImageDraw
from random import randint
import sqlite3
import asyncio
#import string
#import json
#from discord.ext.commands.core import has_permissions
#from discord.message import PartialMessage
#from discord.utils import find
#from discord.ext.commands.errors import CheckFailure, CommandOnCooldown
import io
import aiohttp



client = commands.Bot(command_prefix='.')#,help_command=commands.MinimalHelpCommand())

golamount = 1
@client.event
async def on_ready():
    print("Bot is ready.")

@client.command()
async def setamount(ctx, *, amount):
    global golamount
    golamount = int(amount)

    await ctx.send("Success.")


@client.command()
async def remind(ctx, *, time):

    for x in range(golamount):
        time = int(time)
        await asyncio.sleep(time)
        await ctx.send(f'{ctx.author.mention} you wanted me to remind you of something.')
        await ctx.send(f"{x+1} times this command has been run.")

@client.command()
async def image(ctx):
    

    async with aiohttp.ClientSession() as session:
        async with session.get("https://miro.medium.com/max/1106/1*xBbxi0U2SD40anxuO4s3Fw.jpeg") as resp:
            if resp.status != 200:
                return await ctx.send('could not download file...')
            data = io.BytesIO(await resp.read())
            await ctx.send(file=discord.File(data, 'cool_image.png'))


client.run("ODcwODAzNzUwMjQ2MzA5ODk4.YQSFMA.b_WKCdsNRaKEcvhYnd8zgcMlhm0")

