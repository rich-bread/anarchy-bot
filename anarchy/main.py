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


import command.menu.block as menublock
import mod.discord_module as dismod
#一時的コマンド
@bot.command(name="giveleader")
async def give_leaderRole(ctx):
    leaderId_list = open_json('./s13_leaderlist.json')

    for id in leaderId_list:
        try:
            user = discord.utils.get(ctx.guild.members, id=id)
            role = discord.utils.get(ctx.guild.roles, name='リーダー')
            await user.remove_roles(role)
        except Exception as e:
            await ctx.send(embed=dismod.error(e))

        try:
            await user.add_roles(role)
        except Exception as e:
            await ctx.send(embed=dismod.error(e))
        else:
            await ctx.send(embed=dismod.success(f"Added leader role to {user}."))

import mutual.log as log
bot.add_cog(log.send(bot))


@bot.command()
async def errorcheck(ctx):
    try:
        raise ZeroDivisionError
    except Exception as e:
        await log.send().error(e)
            

bot.run(token)