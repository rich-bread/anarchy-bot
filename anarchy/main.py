import discord
from discord.ext import commands, tasks

from mod.json_module import open_json

#appsettings.json
settings = open_json('./appsettings.json')

#botの情報を取得
prefix = settings['prefix']
token = settings['token']

#全てのインテントを有効化
intents = discord.Intents.all()

#botを作成
bot = commands.Bot(intents=intents, command_prefix=prefix)

#起動時処理
@bot.event
async def on_ready():
    print("Login.")

import command.menu.menu as menu
@bot.command(name="menu")
async def menu_console(ctx):
    await menu.general(bot, ctx)

bot.run(token)