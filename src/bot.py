import math
import json
from datetime import datetime

import asyncio
import brawlstats as bs
import discord
from discord.ext import commands

star_skins = {
    "Gold Mecha Bo": 50000,
    "Light Mecha Bo": 10000,
    "Gold Mecha Crow": 50000,
    "Light Mecha Crow": 50000,
    "Linebacker Bull": 2500,
    "Outlaw Colt": 500
}

firestar493_tag = "GJOYQJR8"

bot_prefixes = ("sp ", "Sp ", "SP ", "sP ")
bot = commands.Bot(
    bot_prefixes,
    case_insensitive=True,
    activity=discord.Game(name="sp help | Firestar493#6963"))

def calc_rank_star_points(player):
    total = 0
    for brawler in player.brawlers:
        if brawler.rank >= 20:
            total += 600
        elif brawler.rank >= 15:
            total += 300
        elif brawler.rank >= 10:
            total += 100
    return total

def calc_season_star_points(player):
    total = 0
    for brawler in player.brawlers:
        total += max(0, math.ceil((brawler.trophies - 500) / 2))
    return total

def count_selected_star_skins(player):
    total = 0
    for brawler in player.brawlers:
        if brawler.skin in star_skins:
            total += 1
    return total

def calc_selected_star_skins_cost(player):
    total = 0
    for brawler in player.brawlers:
        total += star_skins.get(brawler.skin, 0)
    return total

with open("tokens/brawlstats.txt") as f:
    bs_client = bs.Client(
        f.read().strip(),
        is_async=True,
        prevent_ratelimit=True,
        loop=bot.loop)

def clean_tag(tag):
    return tag.strip().replace("#", "")

async def is_valid_player(tag):
    try:
        _ = await bs_client.get_player(clean_tag(tag))
        return True
    except bs.errors.NotFoundError:
        return False

def get_player_tag_from_discord_id(discord_id):
    with open("../data/profiles.json") as f:
        tag = json.load(f).get(str(discord_id), "")
    return tag

async def get_player(ctx, tag="", verbose=False):
    has_mentions = len(ctx.message.mentions) > 0
    discord_id = ctx.message.mentions[0].id if has_mentions else ctx.author.id
    if has_mentions or len(tag) == 0:
        tag = get_player_tag_from_discord_id(discord_id)
    if len(tag) == 0:
        if verbose:
            tip_message = (
                f"{ctx.message.mentions[0]} has not set up their profile. Tell them to use `sp set`!" if has_mentions
                else "Use `sp set` to associate your Discord account with your Brawl Stars profile.")
            await ctx.send(tip_message)
        return None
    try:
        player = await bs_client.get_player(clean_tag(tag))
        return player
    except bs.errors.NotFoundError:
        if verbose:
            await ctx.send(f"Sorry, the tag {tag} is not a valid player tag.")
        return None

@bot.event
async def on_ready():
    print("Ready to count some star points!")
    print(datetime.now())

@bot.command(name="invite")
async def cmd_invite(ctx):
    """Sends an invite link to invite the bot to other servers"""
    await ctx.send("https://discordapp.com/api/oauth2/authorize?client_id=599834923976622100&permissions=378944&scope=bot")

@bot.command(name="set")
async def cmd_set(ctx, tag=""):
    """Associates the Discord account using the command with the Brawl Stars tag given."""
    tag = clean_tag(tag)
    if len(tag) == 0:
        await ctx.send(f"Enter a player tag after your command. e.g. `sp set #{firestar493_tag}`")
        return
    try:
        player = await bs_client.get_player(tag)
    except bs.errors.NotFoundError:
        await ctx.send(f"Sorry, the tag {tag} is not a valid player tag.")
        return
    with open("../data/profiles.json") as f:
        profile_data = json.load(f)
    profile_data[str(ctx.author.id)] = tag
    with open("../data/profiles.json", "w") as f:
        json.dump(profile_data, f)
    await ctx.send(f"{ctx.author.mention} Your profile is now associated with {player.name} (#{tag})")

@bot.command(name="count")
async def cmd_count(ctx, tag=""):
    """Calculates the number of star points a player with a given tag will receive."""
    player = await get_player(ctx, tag, verbose=True)
    if player is not None:
        await ctx.send(f"Star points that **{player.name}** will earn this season: {calc_season_star_points(player)}")

with open("tokens/bot.txt") as f:
    bot.run(f.read().strip())
