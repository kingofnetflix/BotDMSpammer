import random
import discord
import aiohttp
import asyncio
from discord import app_commands
from discord.ext import commands

intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)
with open('owners.txt', 'r') as file:
    owner = [int(line.strip()) for line in file]
with open('tokens.txt', 'r') as file:
    tokens = [str(line.strip()) for line in file]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.tree.command(name="checkbots", description="check the amount of bots in the db")
async def check_bots(interaction: discord.Interaction):
    with open('tokens.txt', 'r') as file:
        tokens = file.read().splitlines()
    token_count = len(tokens)
    await interaction.response.send_message(f'Currently, we have {token_count} amount of bots.')

@bot.tree.command(name="addtoken", description="add tokens to the db")
async def add_token(interaction: discord.Interaction, new_token: str):
    with open('tokens.txt', 'r') as file:
        tokens = [str(line.strip()) for line in file]
    with open('owners.txt', 'r') as file:
        owner = [int(line.strip()) for line in file]
    if not interaction.user.id in owner:
        await interaction.response.send_message('no')
        return
    
    if not await is_valid_bot_token(new_token):
        await interaction.response.send_message('Invalid bot token. Please make sure it corresponds to a real Discord bot.')
        return
    
    if new_token in tokens:
        await interaction.response.send_message('This token is already in the database.', ephemeral=True)
        return

    with open('tokens.txt', 'a') as file:
        file.write('\n' + new_token)
    await interaction.response.send_message('Token added successfully.', ephemeral=True)

@bot.tree.command(name="addowner", description="add owner to the db")
async def add_owner(interaction: discord.Interaction, new_owner: discord.User):
    with open('owners.txt', 'r') as file:
        owner = [int(line.strip()) for line in file]

    if not interaction.user.id in owner:
        await interaction.response.send_message('no')
        return
        
    if new_owner.id in owner:
        await interaction.response.send_message('This user is already an owner.')
        return

    with open('owners.txt', 'a') as file:
        owner.write('\n' + str(new_owner.id))
    await interaction.response.send_message('Owner added successfully.')

async def is_valid_bot_token(token):
    headers = {
        'Authorization': f'Bot {token}',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('https://discord.com/api/v10/users/@me', headers=headers) as resp:
            return resp.status == 200

async def send_dm(session, token, user_id, content, delay, proxy):
    headers = {
        'Authorization': f'Bot {token}',
        'Content-Type': 'application/json',
    }
    payload = {
        'recipient_id': user_id,
        'content': content,
    }
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as client_session:
        async with client_session.post(f'https://discord.com/api/v10/users/@me/channels', headers=headers, json=payload) as resp:
            data = await resp.json()
            channel_id = data.get('id')

            if channel_id:
                await asyncio.sleep(delay)
                async with client_session.post(f'https://discord.com/api/v10/channels/{channel_id}/messages', headers=headers, json=payload) as _:
                    pass

async def get_user_avatar_url(user_id):
    user = await bot.fetch_user(user_id)
    return user.avatar.url

@bot.tree.command(name="mass", description="mass dm someone with all of the bots in our db")
async def mass_message(interaction: discord.Interaction, user: discord.User, message: str, delay: int = 0):
    with open('owners.txt', 'r') as file:
        owner = [int(line.strip()) for line in file]
    if not interaction.user.id in owner:
        await interaction.response.send_message('no')
        return

    user_avatar_url = await get_user_avatar_url(1177026955959337063)
    embed = discord.Embed(
        title="Spam Interface",
        description=f"Attempting to spam {user.mention}",
        color=discord.Color.random()
    )
    embed.set_footer(text=f'Made by KingOfNetflix (discord: derxys)', icon_url=user_avatar_url)
    await interaction.response.send_message(embed=embed)
    tokens = []
    with open('tokens.txt', 'r') as file:
        tokens = file.read().splitlines()

    proxies = []
    proxy_file = 'proxies.txt'
    try:
        with open(proxy_file, 'r') as proxy_file:
            proxies = proxy_file.read().splitlines()
    except FileNotFoundError:
        await interaction.response.send_message(f'The bot has crashed into an error. Please report this error to admins: The specified proxy file "{proxy_file}" does not exist.')
        return

    async with aiohttp.ClientSession() as session:
        for index, token in enumerate(tokens):
            await send_dm(session, token, user.id, message, delay if index > 0 else 0, random.choice(proxies))
            await asyncio.sleep(delay)

@bot.tree.command(name="reload", description="reload slash commands")
async def test(interaction: discord.Interaction):
    if not interaction.user.id in owner:
        await interaction.response.send_message('no')
        return
    await bot.tree.sync()
    await interaction.response.send_message("reloaded slash commands")

@bot.tree.command(name="say", description="say something through the bot")
async def test(interaction: discord.Interaction, message: str):
    if not interaction.user.id in owner:
        await interaction.response.send_message('no')
        return
    await interaction.response.send_message(message)

bot.run('MTE5NjE1MDA0NDEzMTMzNjQxMw.GxuwUf.Xm8nAjtEV42qwL9a9Z4uoRjjjtDhgKK7Cw8sjI')
