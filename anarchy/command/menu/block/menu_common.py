import discord
import requests, asyncio
from typing import Union

import mod.discord_module as dismod

from mod.json_module import open_json

import command.menu.block.regis as regis

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
        message = await bot.wait_for('message', check=check, timeout=180.0)
    except asyncio.TimeoutError:
        error = await channel.send(embed=dismod.error("待機時間内にメッセージが送信されませんでした"))
        return None
    else:
        return message.content


#ユーザからのメッセージ確認(省略型)
async def await_message(bot, channel, author, title, content):
   bot_msg = await channel.send(embed=dismod.default(title, content))
   message = await check_message(bot, channel, author)
   return message


#ユーザからのリアクション確認
async def check_reaction(bot, channel, author, emoji_list, forcequit=False):
    count=0
    while count < 1:
        def check(r: discord.Reaction, u: Union[discord.Member, discord.User]):
            return u.id == author.id and r.message.channel.id == channel.id and \
               str(r.emoji) in emoji_list
        try:
            reaction, user = await bot.wait_for(event='reaction_add', check=check, timeout=180.0)
        except asyncio.TimeoutError:
            await channel.send(embed=dismod.error("待機時間内にリアクションが確認できませんでした"))
            return None
        else:
            if user != author: continue

            if forcequit == True and reaction.emoji == emoji_list[-1]:
                await channel.send(embed=dismod.default("終了", "終了ボタンが押されました。プログラムを終了します"))
                return None

            count+=1

    return reaction.emoji


#ユーザからのリアクション確認(省略型)
async def await_reaction(bot, channel, author, emoji_list, title, content, forcequit=False):
    bot_msg = await channel.send(embed=dismod.default(title, content))
    for e in emoji_list: await bot_msg.add_reaction(e)
    reaction = await check_reaction(bot, channel, author, emoji_list, forcequit)
    return reaction


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

    q_idenfitcation = await channel.send(embed=dismod.default("変更対象", \
                                        "変更するメンバーは本人ですか？\r\n" + '\r\n'.join(descriptions)))
    for r in reactions: await q_idenfitcation.add_reaction(r)

    reaction = await check_reaction(bot, channel, author, reactions)
    if reaction == None: return reaction

    if reaction == reactions[0]: return author
    else:
        count=0
        while count<1:
            q_mention = await channel.send(embed=dismod.default("チーム確認", \
                                            "変更したいメンバーをメンションしてください(※このサーバーに参加している必要があります"))
            mention = await check_message(bot, channel, author)
            if mention == None: return

            if "<@" not in mention:
                await channel.send(embed=dismod.error("正しいメンションではありません。再度入力してください"))
                await q_mention.delete()
                continue
            else:
                count+=1

        userid = id_fromMention(mention)
        response = await regis.verify_team('check-team', author.id, userid)

        user = await get_user(bot, userid)

        if response.status_code == 200: return user
        else:
            await channel.send(embed=dismod.error("同じチームに所属していることを確認することができませんでした。同じチームに所属しているのにも関わらず"+\
                                                  "エラーが出た場合は、 <@754653200757424149> までご連絡ください"))
            return None


#ユーザデータが存在するか確認
async def presence_userdata(id):
    data = (await regis.get_db('read', 'indiv', id, 'all')).json()
    print(data)

    if data != None: return True
    else: return False