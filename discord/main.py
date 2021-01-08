from dotenv import load_dotenv
import os
import requests
from mcstatus import MinecraftServer

import discord
from discord.ext import commands
from discord.ext import tasks

import asyncio
from datetime import datetime

#  Setup Sentry.
import sentry_sdk
sentry_sdk.init(
    "https://863b3e8a8dfa405cbd9ad6fae453ab2d@o352799.ingest.sentry.io/5584050",
    traces_sample_rate=1.0
)


# Load configuration.
load_dotenv()
SERVER_HOSTNAME = os.getenv("SERVER_HOSTNAME")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
WATCHDOG_CHANNEL = os.getenv("WATCHDOG_CHANNEL")


# Create bot client.
intents = discord.Intents.default()
client = commands.Bot(command_prefix="/mc", intents=intents)


# Check if server is up.
def is_online():
    try:
        MinecraftServer.lookup(SERVER_HOSTNAME).ping()

        return True
    except:
        return False


last_activity = datetime.timestamp(datetime.now())


@tasks.loop(minutes=1)
async def watchdog():
    global last_activity

    if is_online:
        minecraft_status = MinecraftServer.lookup(SERVER_HOSTNAME).status()

        if minecraft_status.players.online == 0:
            print("No players logged in!")
            print("Time of Inactivity:", datetime.timestamp(datetime.now()) - last_activity)

            # Change Bot activity!
            activity = discord.Activity(name="for a player to join!", type=discord.ActivityType.watching)
            await client.change_presence(activity=activity)

            if (datetime.timestamp(datetime.now()) - last_activity) > 900:

                print("Watchdog: Destroying server!")

                channel = client.get_channel(WATCHDOG_CHANNEL)
                embed = discord.Embed(title=":skull_crossbones:   Server Watchdog",
                                      description="Destroying the server after 15 minutes of inactivity!\n\nThis process can't be stopped now!\n", color=0xff344a)
                embed.set_author(name="Minecraft Server Manager")
                embed.set_footer(text="As for {}".format(datetime.now().strftime("%H:%M, %m/%d/%Y")))
                embed.add_field(name="Status", value="Sending Request")

                msg = await channel.send(embed=embed)
                await msg.add_reaction("📡")

                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": f"token { GITHUB_TOKEN }",
                }

                req = requests.post("https://api.github.com/repos/RangerDigital/tassadar/actions/workflows/destroy_tassadar.yml/dispatches", json={"ref": "master"}, headers=headers)

                if req.status_code == 204:
                    embed.set_field_at(0, name="Status", value="Destroying Server")
                    await msg.add_reaction("🔥")
                    await msg.edit(embed=embed)

                timeout = 0
                while not is_online() or timeout > 300:
                    timeout += 1
                    await asyncio.sleep(1)

                else:
                    if timeout > 300:
                        embed.set_field_at(0, name="Status", value="Failure")
                        await msg.add_reaction("❌")

                    else:
                        embed.set_field_at(0, name="Status", value="Destroyed")
                        await msg.add_reaction("☠")

                    await msg.edit(embed=embed)
        else:
            last_activity = datetime.timestamp(datetime.now())

            # Change Bot activity!
            activity = discord.Activity(name=f"{ minecraft_status.players.online } players play on the server!", type=discord.ActivityType.watching)
            await client.change_presence(activity=activity)
    else:
        # Change Bot activity!
        activity = discord.Activity(name="for /mcstart command!", type=discord.ActivityType.listening)
        await client.change_presence(activity=activity)


@client.event
async def on_ready():
    print("Started! Logged in as", client.user.name)

    watchdog.start()


# /status - Sends current server status.
@client.command()
async def status(ctx):
    embed = discord.Embed(title=":crossed_swords:   Server Status", description="The current situation looks like this.\n", color=0xaaff34)
    embed.set_author(name="Minecraft Server Manager")
    embed.set_footer(text="As for {}".format(datetime.now().strftime("%H:%M, %m/%d/%Y")))

    async with ctx.channel.typing():

        if is_online():
            minecraft_status = MinecraftServer.lookup(SERVER_HOSTNAME).status()

            embed.add_field(name="Status", value="Online", inline=False)
            embed.add_field(name="Players", value=minecraft_status.players.online)
            embed.add_field(name="Ping", value="{} ms".format(round(minecraft_status.latency)))

        else:
            embed.color = 0xff344a
            embed.add_field(name="Status", value="Offline")

    await ctx.send(embed=embed)


@client.command()
async def start(ctx):
    async with ctx.channel.typing():
        embed = discord.Embed(title=":cake:   Server Startup", description="The server is being provisioned right now. \n\nThis takes on average 2 minutes.\n", color=0xaaff34)
        embed.set_author(name="Minecraft Server Manager")
        embed.add_field(name="Status", value="Sending Request")
        embed.set_footer(text="This shouldn't take long!")

        if is_online():
            embed.set_field_at(0, name="Status", value="Already Running")
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("🍰")
            return

        msg = await ctx.send(embed=embed)
        await msg.add_reaction("📡")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token { GITHUB_TOKEN }",
    }

    req = requests.post("https://api.github.com/repos/RangerDigital/tassadar/actions/workflows/create_tassadar.yml/dispatches", json={"ref": "master"}, headers=headers)

    if req.status_code == 204:
        embed.set_field_at(0, name="Status", value="Provisioning Server")
        await msg.add_reaction("📦")
        await msg.edit(embed=embed)

    timeout = 0
    while is_online() == False or timeout > 300:
        timeout += 1
        await asyncio.sleep(1)

    else:
        if timeout > 300:
            embed.set_field_at(0, name="Status", value="Failure")
            await msg.add_reaction("❌")

        else:
            embed.set_field_at(0, name="Status", value="Success")
            await msg.add_reaction("🍰")

        await msg.edit(embed=embed)


@client.command()
async def stop(ctx):
    async with ctx.channel.typing():
        embed = discord.Embed(title=":skull_crossbones:   Server Shutdown", description="The server is being destroyed right now. \n", color=0xff344a)
        embed.set_author(name="Minecraft Server Manager")
        embed.add_field(name="Status", value="Sending Request")
        embed.set_footer(text="Thanks for saving my money!")

        # If already destroyed return.
        if not is_online():
            embed.set_field_at(0, name="Status", value="Already Destroyed")
            msg = await ctx.send(embed=embed)

            await msg.add_reaction("☠")
            return

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("📡")

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token { GITHUB_TOKEN }",
    }

    req = requests.post("https://api.github.com/repos/RangerDigital/tassadar/actions/workflows/destroy_tassadar.yml/dispatches", json={"ref": "master"}, headers=headers)

    if req.status_code == 204:
        embed.set_field_at(0, name="Status", value="Destroying Server")
        await msg.add_reaction("🔥")
        await msg.edit(embed=embed)

    timeout = 0
    while not is_online() or timeout > 300:
        timeout += 1
        await asyncio.sleep(1)

    else:
        if timeout > 300:
            embed.set_field_at(0, name="Status", value="Failure")
            await msg.add_reaction("❌")

        else:
            embed.set_field_at(0, name="Status", value="Destroyed")
            await msg.add_reaction("☠")

        await msg.edit(embed=embed)


client.run(DISCORD_TOKEN)
