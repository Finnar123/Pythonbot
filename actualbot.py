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

@client.command()
async def image(ctx):
    await ctx.send("sending an image")
    await ctx.send(file="data:image/jpeg;base64,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")
    

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
