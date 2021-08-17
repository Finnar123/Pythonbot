import discord
import random
from discord import activity, Client
from discord import channel
from discord.ext import commands, tasks
from discord.ext.commands import cooldown, BucketType, MissingPermissions
from PIL import Image, ImageFont, ImageDraw
from random import randint
import sqlite3
import asyncio
import string
import json
from discord.ext.commands.core import has_permissions
from discord.utils import find
from discord.ext.commands.errors import CheckFailure, CommandOnCooldown

#client = commands.Bot(command_prefix=".")


def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix=get_prefix)

card1series = ""
card1char = ""
card1number = 0
card2series = ""
card2char = ""
card2number = 0
card3series = ""
card3char = ""
card3number = 0
placeholder = ""
place2holder = ""
place3holder = ""
grab = True

checkgrabbed = {}
firstreact1 = 0
firstreact2 = 0
firstreact3 = 0

count = 0

checkedchannel = 0

conn2 = sqlite3.connect('userdata.db')
c2 = conn2.cursor()

timeout = False


class User:

    def __init__(self, series, char, printid, uniqueid, placeholder):
        self.series = series
        self.char = char
        self.printid = printid
        self.uniqueid = uniqueid
        self.placeholder = placeholder

    def insertintotable(self, user_id):
        c2.execute("INSERT INTO userdata VALUES (?,?,?,?,?,?)",
                   (user_id, self.char, self.series, self.printid, self.uniqueid, self.placeholder))
        conn2.commit()


def generatingunique():

    while True:
        length = 5
        char = string.ascii_uppercase + string.digits + string.ascii_lowercase
        code = ''.join(random.choice(char) for x in range(length))

        c2.execute("SELECT * FROM userdata WHERE uniqueid=?", (code,))

        if c2.fetchone() == None:
            return code
        else:
            continue


def generate_cards():

    conn = sqlite3.connect('cards.db')
    c = conn.cursor()

    card = 0

    while card < 3:

        c.execute("SELECT * FROM cards")
        lists = (c.fetchall())

        cards = randint(0, len(lists)-1)
        image = Image.open("frame-brass.jpg")
        insertedimage = Image.open(lists[cards][3])
        inserted = insertedimage.resize((156, 153))
        inserted.save(lists[cards][3])

        image.paste(inserted, (22, 70))

        title_font = ImageFont.truetype("arial.ttf", 30)  # text size

        series = lists[cards][1]
        char = lists[cards][0]
        number = lists[cards][2]

        number = int(number)
        number += 1

        num_font = ImageFont.truetype("arial.ttf", 10)

        image_editable = ImageDraw.Draw(image)

        image_editable.text((35, 35), char, (0, 0, 0), font=title_font)
        image_editable.text((35, 230), series, (0, 0, 0), font=title_font)
        image_editable.text((124, 275), str(number),
                            (255, 255, 255), font=num_font)

        c.execute("UPDATE cards SET printid=? WHERE characters=?",
                  (str(number), char))
        conn.commit()

        if card == 0:
            image.save("frameresult1.jpg")
            res1 = image.copy()
            global card1series, card1char, card1number, placeholder
            card1series, card1char, card1number, placeholder = lists[cards]
            card1number = number
        elif card == 1:
            image.save("frameresult2.jpg")
            res2 = image.copy()
            global card2series, card2char, card2number, place2holder
            card2series, card2char, card2number, place2holder = lists[cards]
            card2number = number

        elif card == 2:
            image.save("frameresult3.jpg")
            res3 = image.copy()
            global card3series, card3char, card3number, place3holder
            card3series, card3char, card3number, place3holder = lists[cards]
            card3number = number

        card += 1

    #   image.paste(inserted, (22, 70))

    newimage = Image.open("newimage.jpg")
    newimage = newimage.resize((602, 296))
    newimage.paste(res1)
    newimage.paste(res2, (201, 0))
    newimage.paste(res3, (401, 0))

    newimage.save("newimage.jpg")


def isrightchannel(ctx):

    with open('channel.json', 'r') as f2:
        channels = json.load(f2)

    if ctx.channel.id != channels[str(ctx.guild.id)]:
        return False
    else:
        return True


# --------------------- prefixes and setchannel ------------------


@client.event
async def on_guild_join(guild):

    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '.'

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f)

    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('Hello, my prefix is "." ')
        await general.send("Please set a channel for me to spawn in using **setchannel** command.")

    # setchannel
    # with open('channel.json', 'r') as f2:
    #     channels = json.load(f2)

    # with open('channel.json', 'w') as f2:
    #     json.dump(channels, f2)


@client.event
async def on_guild_remove(guild):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f)

# set channel
    with open('channel.json', 'r') as f2:
        channels = json.load(f2)

    channels.pop(str(guild.id))

    with open('channel.json', 'w') as f2:
        json.dump(channels, f2)

    # pass
    # add a message on join that tells that you have to set a channel


@client.command()
@has_permissions(manage_channels=True)
async def changeprefix(ctx, prefix):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open('prefixes.json', 'w') as f:
        json.dump(prefixes, f)

    await ctx.send(f'Prefix changed to: {prefix}')


@changeprefix.error
async def changeprefix_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You need manage channel perms to use this command.")


@client.command()
@has_permissions(manage_channels=True)
async def setchannel(ctx, *, channel: discord.TextChannel):

    for channelname in ctx.guild.channels:
        if channelname == channel:

            with open('channel.json', 'r') as f2:
                channels = json.load(f2)

            channels[str(ctx.guild.id)] = channelname.id

            with open('channel.json', 'w') as f2:
                json.dump(channels, f2)

            await ctx.send(f"Success! The bot will now spawn in {channel}")


@setchannel.error
async def setchannel_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You need manage channel perms to use this command.")


# -------------------- prefixes ----------------------


@client.command()
async def invite(ctx):
    await ctx.send("You can invite the bot using: https://discord.com/api/oauth2/authorize?client_id=870803750246309898&permissions=0&scope=bot")


@client.event
async def on_ready():

    print("Bot is ready.")
    print("Make sure to set a channel everytime bot is run.")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    try:
        with open('channel.json', 'r') as f2:
            channels = json.load(f2)

    # change this to grab database int
            sendhere = client.get_channel(channels[str(message.guild.id)])
    except:
        await client.process_commands(message)
        return

    global count
    count += 1

    # await message.channel.send(f"for every message {count}")

    if count > 5:

        count = 0

        title = await sendhere.send("I am dropping some cards because this server is active.")

        generate_cards()

        uniqueid1 = generatingunique()
        uniqueid2 = generatingunique()
        uniqueid3 = generatingunique()

        global timeout
        timeout = False

        global user1, user2, user3
        user1 = User(card1char, card1series,
                     card1number, uniqueid1, placeholder)
        user2 = User(card2char, card2series, card2number,
                     uniqueid2, place2holder)
        user3 = User(card3char, card3series, card3number,
                     uniqueid3, place3holder)

        global firstreact1, firstreact2, firstreact3
        firstreact1 = 0
        firstreact2 = 0
        firstreact3 = 0

        msg = await sendhere.send(file=discord.File("newimage.jpg"))

        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        await msg.add_reaction("3️⃣")

        await asyncio.sleep(30)
        await title.edit(content="These cards can no longer be grabbed.")

        timeout = True

    await client.process_commands(message)


@client.command(aliases=['d'])
@commands.check(isrightchannel)
@cooldown(1, 5, BucketType.user)
async def drop(ctx):
    # ctx.author.id

    title = await ctx.send(f"{ctx.author.mention} is dropping 3 cards")

    generate_cards()

    uniqueid1 = generatingunique()
    uniqueid2 = generatingunique()
    uniqueid3 = generatingunique()

    global timeout
    timeout = False

    global user1, user2, user3
    user1 = User(card1char, card1series, card1number,
                 uniqueid1, placeholder)
    user2 = User(card2char, card2series, card2number, uniqueid2, place2holder)
    user3 = User(card3char, card3series, card3number, uniqueid3, place3holder)

    global firstreact1, firstreact2, firstreact3
    firstreact1 = 0
    firstreact2 = 0
    firstreact3 = 0

    msg = await ctx.send(file=discord.File("newimage.jpg"))

    await msg.add_reaction("1️⃣")
    await msg.add_reaction("2️⃣")
    await msg.add_reaction("3️⃣")

    # should be 60
    await asyncio.sleep(30)
    await title.edit(content="These cards can no longer be grabbed.")

    timeout = True


@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author != client.user:
        return

    if timeout:
        return

    global grab
    global firstreact1, firstreact2, firstreact3
    channel = reaction.message.channel

    if grab:
        pass
    else:
        return

    # # fights, a work in progress

    if user.id in checkgrabbed.keys():
        if 'grabbed' in checkgrabbed.values():
            await channel.send(f"{user.mention} you currently are on grab cooldown.")
            grab = False
            await asyncio.sleep(10)
            grab = True
            checkgrabbed[user.id] = 'available'
            await channel.send(f"{user.mention} you can grab cards now. (seen)")
            return

    if reaction.count == 1:
        pass
    else:
        if reaction.emoji == "1️⃣" and user.id != "870803750246309898" and firstreact1 == 0:
            firstreact1 += 1
            await channel.send(
                f"You have grab {user1.char} and it's print is {user1.printid} and it was grabbed by {user.mention} and its card code is {user1.uniqueid}"
            )
            user1.insertintotable(user.id)
            grabbed1 = {user.id: 'grabbed'}
            checkgrabbed.update(grabbed1)
        # user.id = id

        elif reaction.emoji == "2️⃣" and user.id != "870803750246309898" and firstreact2 == 0:
            firstreact2 += 1
            await channel.send(
                f"You have grab {user2.char} and it's print is {user2.printid} and it was grabbed by {user.mention} and its card code is {user2.uniqueid}"
            )
            user2.insertintotable(user.id)
            grabbed2 = {user.id: 'grabbed'}
            checkgrabbed.update(grabbed2)

        elif reaction.emoji == "3️⃣" and user.id != "870803750246309898" and firstreact3 == 0:
            firstreact3 += 1

            await channel.send(
                f"You have grab {user3.char} and it's print is {user3.printid} and it was grabbed by {user.mention} and its card code is {user3.uniqueid}"
            )
            user3.insertintotable(user.id)
            grabbed3 = {user.id: 'grabbed'}
            checkgrabbed.update(grabbed3)

    # checkgrabbed[client.user.id] = "No"

    if user.id in checkgrabbed.keys():
        if 'grabbed' in checkgrabbed.values():
            # print(checkgrabbed)
            await asyncio.sleep(10)
            checkgrabbed[user.id] = 'available'
            await channel.send(f"{user.mention} you can grab cards now. (hidden)")
            return


@drop.error
async def drop_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        await ctx.send(f"Your drop is on cooldown. Try again in {error.retry_after:,.2f} seconds.")


@client.command()
@cooldown(1, 1, BucketType.user)
async def view(ctx, *, unique):

    c2.execute("SELECT * FROM userdata WHERE uniqueid=?", (unique,))
    uniquecard = c2.fetchall()

    user = await client.fetch_user(uniquecard[0][0])

    embed = discord.Embed(
        title=f"{user.name}'s card", description=f"Owned by {user.name}", color=discord.Colour.blue())

    embed.add_field(name=f"Name: {uniquecard[0][1]}",
                    value=f"ID: {uniquecard[0][4]} **Series**: {uniquecard[0][2]} **Print** : {uniquecard[0][3]}", inline=False)

    file = discord.File(uniquecard[0][5])
    embed.set_image(url=f"attachment://{uniquecard[0][5]}")

    await ctx.send(embed=embed, file=file)


@client.command()
async def myinv(ctx):
    embed = discord.Embed(
        title=f"{ctx.author.name} collection", description=f"cards carried by {ctx.author.mention}", color=discord.Colour.red())

    c2.execute("SELECT * FROM userdata WHERE userid=?", (ctx.author.id,))
    userscards = c2.fetchall()

    for cards in range(len(userscards)):
        embed.add_field(name=f"Unique ID: {userscards[cards][4]}",
                        value=f"**Character**: {userscards[cards][1]} **Series**: {userscards[cards][2]} **Print** : {userscards[cards][3]}", inline=False)

    await ctx.send(embed=embed)


@client.command()
async def inv(ctx, member: discord.Member):
    embed = discord.Embed(
        title=f"{member.name} collection", description=f"cards carried by {member.mention}", color=discord.Colour.red())
    c2.execute("SELECT * FROM userdata WHERE userid=?", (member.id,))
    userscards = c2.fetchall()

    for cards in range(len(userscards)):
        embed.add_field(name=f"Unique ID: {userscards[cards][4]}",
                        value=f"**Character**: {userscards[cards][1]} **Series**: {userscards[cards][2]} **Print** : {userscards[cards][3]}", inline=False)

#    embed.add_field(name="blank", value="blah blah", inline=False)

    await ctx.send(embed=embed)


@client.command()
@commands.is_owner()
# async def addCharacter(ctx, *, name, series, printid, image):
async def addCharacter(ctx, *, everything):
    every = everything.split("|")

    conn9 = sqlite3.connect('cards.db')
    c9 = conn9.cursor()
    # Joker, Batman, 1, joker.jpg,
    # NAME SERIES PRINT IMAGE
    c9.execute("INSERT INTO cards VALUES (?,?,?,?)",
               (every[0], every[1], 0, every[3]))

    conn9.commit()
    conn9.close()

    await ctx.send("Success! I have added the character.")


@client.command()
@commands.is_owner()
async def ResetDataBase(ctx):

    conn5 = sqlite3.connect('userdata.db')
    c5 = conn5.cursor()

    c5.execute("DELETE from userdata")
    conn5.commit()

    conn5.close()

    await ctx.send("Database has been successfully deleted.")


@client.command()
@commands.is_owner()
async def ResetPrint(ctx):
    conn4 = sqlite3.connect('cards.db')
    c4 = conn4.cursor()

    c4.execute("UPDATE cards SET printid=?", (0,))

    conn4.commit()
    conn4.close()

    await ctx.send("Card Prints have been successfully reset.")


@ResetDataBase.error
async def ResetDataBase_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You are not allowed to use this command.")


@ResetPrint.error
async def ResetPrint_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You are not allowed to use this command.")


@addCharacter.error
async def addCharacter_error(ctx, error):
    if isinstance(error, CheckFailure):
        await ctx.send("You are not allowed to use this command.")


client.run("ODcwODAzNzUwMjQ2MzA5ODk4.YQSFMA.b_WKCdsNRaKEcvhYnd8zgcMlhm0")

# referencing my compelicated way to add cooldown
# ctx.author.id
#checkdropped = {}
#dropisaval = True
#global dropisaval

# if dropisaval:
#     pass
# else:
#     return

# if ctx.author.id in checkdropped.keys():
#     if 'dropped' in checkdropped.values():
#         await ctx.send(f"{ctx.author.mention} you currently are on drop cooldown.")
#         dropisaval = False
#         await asyncio.sleep(15)
#         checkdropped[ctx.author.id] = 'available'
#         dropisaval = True
#         await ctx.send(f"{ctx.author.mention} you can drop cards now.")
#         return

# await asyncio.sleep(1)

# dropped = {ctx.author.id: 'dropped'}
# checkdropped.update(dropped)


# for grab


# # checkgrabbed = {}
#    if reaction.message.author != client.user:
#         return
#     global grab
#     global first

# need to check if the user id is in the dictionary then take away the users ability to react to that specific message, return it in the next drop
# combine this with grab timer
# make it so 1 user cant grab a card 2 times in a row
# make it so another user cant grab that same card

# if user.id in checkgrabbed.keys():
#     if 'grabbed' in checkgrabbed.values():
#         await channel.send(f"{user.mention} you currently are on grab cooldown.")
#         grab = False
#         await asyncio.sleep(10)
#         grab = True
#         checkgrabbed[user.id] = 'available'
#         await channel.send(f"{user.mention} you can grab cards now.")

# if reaction.count == 1:
#     pass
# else:
#     if reaction.emoji == "1️⃣" and user.id != "870803750246309898" and firstreact1 == 0:
#         firstreact1 += 1
#         await channel.send(
#             f"You have grab {user1.char} and it's print is {user1.printid} and it was grabbed by {user.mention}"
#         )
#         user1.insertintotable(user.id)
#         grabbed1 = {user.id: 'grabbed'}
#         checkgrabbed.update(grabbed1)
#         # user.id = id

#     elif reaction.emoji == "2️⃣" and user.id != "870803750246309898" and firstreact2 == 0:
#         firstreact2 += 1
#         await channel.send(
#             f"You have grab {user2.char} and it's print is {user2.printid} and it was grabbed by {user.mention}"
#         )
#         user2.insertintotable(user.id)
#         grabbed2 = {user.id: 'grabbed'}
#         checkgrabbed.update(grabbed2)

#     elif reaction.emoji == "3️⃣" and user.id != "870803750246309898" and firstreact3 == 0:
#         firstreact3 += 1

#         await channel.send(
#             f"You have grab {user3.char} and it's print is {user3.printid} and it was grabbed by {user.mention}"
#         )
#         user3.insertintotable(user.id)
#         grabbed3 = {user.id: 'grabbed'}
#         checkgrabbed.update(grabbed3)


# ---------------------------------------------------------
# right now cooldown isnt working for .event
# need to find a way to add a cooldown for reactions

# @client.event
# async def on_reaction_add(reaction, user):
#     if reaction.message.author != client.user:
#         return

#     channel = reaction.message.channel

#     users = await reaction.users().flatten()
#     winner = random.choice(users)
#     # fights

#     if reaction.count == 1:
#         pass
#     # elif len(users) > 1:
#         # pass
#     else:
#         if reaction.emoji == "1️⃣" and user.id != "870803750246309898":
#             await channel.send(
#                 f"You have grab {user1.char} and it's print is {user1.printid} and it was grabbed by {user.mention}"
#             )
#             user1.insertintotable(user.id)

#             # user.id = id

#         elif reaction.emoji == "2️⃣" and user.id != "870803750246309898":
#             await channel.send(
#                 f"You have grab {user2.char} and it's print is {user2.printid} and it was grabbed by {user.mention}"
#             )
#             user2.insertintotable(user.id)

#         elif reaction.emoji == "3️⃣" and user.id != "870803750246309898":

#             await channel.send(
#                 f"You have grab {user3.char} and it's print is {user3.printid} and it was grabbed by {user.mention}"
#             )
#             user3.insertintotable(user.id)

#         else:
#             await channel.send("You have already grabbed this card!")

#         # while grab != True:
#         #     await asyncio.sleep(15)
#         #     grab = True


# @client.event
# async def on_command_error(ctx, error):
#     if isinstance(error, CommandOnCooldown):
#         await ctx.send(f"Your grab is on cooldown. Try again in {error.retry_after:,.2f} seconds.")


# RETIRED CODE CHANNEL SPECIFC

# @client.command()
# async def setchannel(ctx, *, channel: discord.TextChannel):
#     global checkedchannel
#     for channelname in ctx.guild.channels:
#         if channelname == channel:
#             checkedchannel = channelname.id
# if channel.isdigit():
#     channelname = client.get_channel(ctx.channel.id)
#     for channelname in ctx.guild.channels:
#         if channelname == client.get_channel(channel):
#             checkedchannel = channel
# else:
#     channel = channel[2:]
#     channel = channel.replace(">", "")
#     channelname = client.get_channel(ctx.channel.id)
#     # await ctx.send(type(channel))
#     # await ctx.send(type(channelname))
#     await ctx.send(client.get_channel(channel))
#     if channel.isdigit():
#         for channelname in ctx.guild.channels:
#             if channelname == client.get_channel(channel):
#                 checkedchannel = channel
#     else:
#         return


# # @client.command()
# # async def graballchannels(ctx):
# #     # await ctx.send(ctx.guild.channels)
# #     place = ctx.guild.channels
# #     await ctx.send(len(place))
# #     for x in ctx.guild.channels:
# #         print(x)react1, firstreact2, firstreact3
#     channel = reaction.message.channel
#     if grab:
#         pass
#     else:
#         return

# global checkedchannel
# print(checkedchannel)
# await checkedchannel.send("This message will always be sent in general2")
