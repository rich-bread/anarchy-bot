import discord
import asyncio

from mod.json_module import open_json
from command.menu.block.menu_common import check_reaction

from mod.discord_module import default
from command.menu.block import indiv, continuous

async def general(bot, ctx):
    role = get_role(ctx)
    frontdesk = await create_frontdesk(ctx, role)
    #frontdesk = ctx.channel

    menu_data = open_json('./command/menu/menu.json')

    emoji_list = [i['emoji'] for i in menu_data if i['implement'] == True]
    description = [f"{i['emoji']} {i['name']}" for i in menu_data if i['implement'] == True]

    await frontdesk.send(f"<@{ctx.author.id}>") #コマンドを実行したユーザにメンション

    count=0
    while count < 1:
        q_menu = await frontdesk.send(embed=default("メニュー", '\r\n'.join(description)))
        for i in emoji_list: await q_menu.add_reaction(i)

        reaction = await check_reaction(bot, frontdesk, ctx.author, emoji_list, True)

        if reaction == None: #タイムアウトor終了リアクションが押された時用
            await frontdesk.send(embed=default("終了", "10秒後にこのチャンネルは削除されます"))
            await asyncio.sleep(10)
            count+=1

        if reaction == "1⃣": #メンバー情報登録・変更
            await indiv.general(bot, ctx, frontdesk)
        elif reaction == "2⃣": #チーム情報登録・変更
            pass
        elif reaction == "3⃣":
            pass
        elif reaction == "4⃣": #継続受付
            await continuous.continued_participation(bot, ctx, frontdesk)

        continue
    
    await ctx.author.remove_roles(role)
    await frontdesk.delete()


        
#BOT使用権のついたロール
def get_role(ctx):
    roleName = "BOT使用" #ロールの名前
    role = discord.utils.get(ctx.guild.roles, name=roleName)
    return role

#受付チャンネルの作成
async def create_frontdesk(ctx,role):
    channelName = "受付チャンネル" #作成するチャンネル名
    categoryName = "FRONTDESK" #カテゴリ名

    frontdesk = await ctx.guild.create_text_channel(channelName)
    category = discord.utils.get(ctx.guild.channels, name=categoryName)
    await frontdesk.edit(category=category)

    await frontdesk.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False) #初期権限設定
    await frontdesk.set_permissions(role, read_messages=True, send_messages=True) #対象ロールの権限変更
    await ctx.author.add_roles(role) #ユーザにロール付与

    return frontdesk