import os
import discord
from discord.ext import commands
from urllib.parse import urlencode
from dotenv import load_dotenv
import requests
import json
import asyncio

load_dotenv(dotenv_path="config")

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

# Define your own list of prohibited words
prohibited_words = ["fuck", "shit", "asshole"]

deleted_users = {}

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()

    # Check if the message contains any prohibited words
    if any(word in content for word in prohibited_words):
        await message.delete()

        user_id = message.author.id
        if user_id in deleted_users:
            deleted_users[user_id] += 1
        else:
            deleted_users[user_id] = 1

    await bot.process_commands(message)

@bot.command()
async def joke(ctx):
    api_url = 'https://api.api-ninjas.com/v1/jokes?limit=1'
    api_token = 'qbMtP+JJrOclrM5STWd2lw==zdBTqThuNANTuTyl'
    headers = {'X-Api-Key': api_token}

    response = requests.get(api_url, headers=headers)
    jokes = json.loads(response.text)

    for joke in jokes:
        await ctx.send(joke['joke'])

@bot.command()
async def mute(ctx, member: discord.Member, duration: int = None):
    if ctx.message.author.guild_permissions.manage_roles:
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

        if not muted_role:
            await ctx.send("Muted role not found. Please create a 'Muted' role.")
            return

        await member.add_roles(muted_role)
        await ctx.send(f"{member.mention} has been muted.")

        if duration:
            await asyncio.sleep(duration)
            await member.remove_roles(muted_role)
            await ctx.send(f"{member.mention} has been unmuted after {duration} seconds.")
    else:
        await ctx.send("You don't have permission to use this command.")


@bot.command()
async def search(ctx):
    await ctx.send("Please provide the following information:")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        await ctx.send("Enter the search name:")
        name = await bot.wait_for('message', check=check, timeout=60)  # Wait for 60 seconds
        name = name.content.lower()

        await ctx.send("Enter the resource type (exams, tests, worksheets, courses):")
        type_ = await bot.wait_for('message', check=check, timeout=60)
        type_ = type_.content.lower()

        await ctx.send("Enter the module name:")
        module = await bot.wait_for('message', check=check, timeout=60)
        module = module.content.lower()

        await ctx.send("Enter the year (1, 2):")
        year = await bot.wait_for('message', check=check, timeout=60)
        year = year.content.lower()

        page = 1
        limit = 20

        api_url = f'https://etc-lib-server.onrender.com/search/?name={name}&type={type_}&module={module}&year={year}&page={page}&limit={limit}'

        response = requests.get(api_url)

        resources = json.loads(response.text)
        if 'error' in resources:
            await ctx.send(resources['error'])
            return

        files = resources['files']

        for file in files:
            url = f'https://drive.google.com/file/d/{file["url"]}'
            await ctx.send(f"{file['name']} URL: {url}")
            await ctx.send('-' * 20)
    except asyncio.TimeoutError:
        await ctx.send("Command timed out. Please try again later.")


bot.run(os.getenv("TOKEN"))

