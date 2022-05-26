import discord
import requests, asyncio
from typing import Union

import mod.discord_module as discord_module

from mod.json_module import open_json

import con.menu.block.regis as regis

#「user」と「author」の使い分け
#userは情報変更等の対象 authorはコマンドを実行している本人


#ユーザオブジェクトの取得
async def get_user(bot,id):
    user = await bot.fetch_user(id)
    return user


#ユーザからのメッセージ確認
async def check_message(bot, channel, author):
    def check(m: discord.Message):
        return m.channel == channel and m.author.id == author.id

    try:
        message = await bot.wait_for('message', check=check, timeout=60.0)
    except asyncio.TimeoutError:
        error = await channel.send(embed=discord_module.error("待機時間内にメッセージが送信されませんでした。"))
        return None
    else:
        return message


#ユーザからのリアクション確認
async def check_reaction(bot, channel, author, emoji_list, forcequit=False):
    count=0
    while count < 1:
        def check(r: discord.Reaction, u: Union[discord.Member, discord.User]):
            return u.id == author.id and r.message.channel.id == channel.id and \
               str(r.emoji) in emoji_list
        try:
            reaction, user = await bot.wait_for(event='reaction_add', check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await channel.send("待機時間内にメッセージが送信されませんでした。")
            return None
        else:
            if user != author: continue

            if forcequit == True and reaction.emoji == emoji_list[-1]:
                await channel.send(embed=discord_module.default("終了", "終了ボタンが押されました。プログラムを終了します"))
                return None

            count+=1

    return reaction.emoji


#メンションからIDの取り出し
def id_fromMention(m:str):
    l = ["<", "@", ">"]
    for i in l:
        m = m.replace(i,'')
    return m


#同じチームに所属しているか確認
async def verify_team(bot, channel, author):

    yon = open_json('./mutual/data/yon.json')
    reactions = [i['emoji'] for i in yon]
    descriptions = [f"{i['emoji']} {i['content']}" for i in yon]

    q_idenfitcation = await channel.send(embed=discord_module.default("変更対象", \
                                        "変更するメンバーは本人ですか？\r\n" + '\r\n'.join(descriptions)))
    for r in reactions: await q_idenfitcation.add_reaction(r)

    reaction = await check_reaction(bot, channel, author, reactions)
    if reaction == None: return reaction

    if reaction == reactions[0]: return author
    else:
        count=0
        while count<1:
            q_mention = await channel.send(embed=discord_module.default("チーム確認", \
                                            "変更したいメンバーをメンションしてください(※このサーバーに参加している必要があります"))
            mention = await check_message(bot, channel, author)

            if "<@" not in mention:
                await channel.send(embed=discord_module.error("正しいメンションではありません。再度入力してください"))
                await q_mention.delete()
                continue
            else:
                count+=1

        userid = id_fromMention(mention)
        response = await regis.verify_team('check-team', author.id, userid)

        user = await get_user(bot, userid)

        if response.status_code == 200: return user
        else: return None