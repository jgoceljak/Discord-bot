import discord
import config
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands
import time
from time import sleep
import asyncio
import variables as g
from multiprocessing import Process
from twitterscrapper import scrapeSearch
import random
import re

checkingForLinks = False
searchChannelID = 1037115746850971670
searchChannel = ""
lastLink = ""

BOT_TOKEN = config.API_KEY
CHANNEL_ID = 1147625399610790039

intents = discord.Intents.default()
intents.presences = True
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("Bot Online")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello! Bot is online")
    try:
        synced = await bot.tree.sync()  # globally sync slash commands
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    sleep(2)


@bot.tree.command(name="ping", description="pong")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)


@bot.tree.command(name="memberinfo", description="Displays User Info")
async def memberinfo(interaction: discord.Interaction, member: discord.Member = None):
    if member == None:
        member = interaction.user
    embed = discord.Embed(title="Member Info")
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Name", value=member.name)
    embed.add_field(name="Status", value=interaction.guild.get_member(member.id).status)
    embed.add_field(name="Creation Date", value=member.created_at.strftime("%m/%d/%Y"))
    await interaction.response.send_message(embed=embed)


@bot.tree.command(
    name="r",
    description="Dice Parsing comman. Insert dice into argument 'd' and adv or dis into 't' ",
)
async def dice(interaction: discord.Interaction, d: str = None, t: str = None):
    rolls = []
    if d == None:
        d = "d20"
        total = random.randint(1, 20)
        rolls.append(total)
        rollType = "None"
    else:
        sides = 0
        modifier = 0
        total = 0
        numberOfDie = 1
        if "d" in d:
            components = re.split("[d+-]", d)
            print(components)
            if components[0] == "":
                numberOfDie = 1
            else:
                numberOfDie = int(components[0])
            sides = int(components[1])
            if "+" in d:
                modifier = int(components[-1])
            if "-" in d:
                modifier = -abs(int(components[-1]))
            for x in range(numberOfDie):
                roll = random.randint(1, sides)
                print(roll)
                rolls.append(roll)
                total += roll
            if t == "adv":
                total = max(rolls) + modifier
                rollType = "Advantage"
            elif t == "dis":
                total = min(rolls) + modifier
                rollType = "Disadvantage"
            else:
                rollType = "None"
                total += modifier

    embed = discord.Embed(title=str(interaction.user) + "'s Dice Roll")
    embed.add_field(name="Final Value:", value="**-->#" + str(total) + "<--**")
    embed.add_field(name="Command:", value=d)
    embed.add_field(name="Roll(s):", value=rolls)
    embed.add_field(name="Rolled With:", value="**" + str(rollType) + "**")
    if 1 in rolls and len(rolls) == 1:
        embed.add_field(name="NAT 1", value="L Bozo")
    if 20 in rolls and len(rolls) == 1:
        embed.add_field(name="NAT 20", value="W Bozo")
    await interaction.response.send_message(embed=embed)

# @bot.tree.command(name="ban", description="Bans a desisgnated user")
# async def ban(interaction: discord.Interaction, user: str):
    
# @bot.tree.command(name="kick", description="Kicks a desisgnated user")
# async def kick(interaction: discord.Interaction, user: str):

@bot.tree.command(
    name="twittersearch",
    description="Searches for new posts for a twitter search on a given interval",
)
async def twitterSearch(interaction: discord.Interaction, interval: int = None):
    global checkingForLinks
    global searchChannelID
    global searchChannel
    if interval == None:
        g.searchInterval = 600
    else:
        g.searchInterval = interval * 60
    print(g.searchInterval)
    scrapingLoop.change_interval(seconds=g.searchInterval)
    searchChannelID = interaction.channel.id
    int(searchChannelID)
    searchChannel = bot.get_channel(searchChannelID)
    await searchChannel.send(
        "Setting search parameters: Interval: " + str(g.searchInterval) + " seconds"
    )
    g.searchScrapping = True
    g.doStartSearch = True
    if __name__ == "__main__":
        p1 = Process(target=scrapeSearch)
        p1.start()
    if checkingForLinks == False:
        scrapingLoop.start()
        checkingForLinks = True


@tasks.loop(seconds=g.searchInterval)
async def scrapingLoop():
    global lastLink
    global searchChannelID
    global searchChannel
    print(searchChannel)
    print("running loop")
    f = open("recentlink.txt", "r")
    link = f.read()
    if lastLink != link:
        searchChannel = bot.get_channel(searchChannelID)
        await searchChannel.send(str(link))
        lastLink = link
    else:
        searchChannel = bot.get_channel(searchChannelID)
        await searchChannel.send(
            "No new posts found in the last " + str(g.searchInterval) + " minutes"
        )


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
