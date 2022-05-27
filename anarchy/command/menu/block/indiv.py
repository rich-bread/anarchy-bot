import discord

from command.menu.block import regis
import mod.discord_module as discord_module
from command.menu.block.menu_common import check_message, check_reaction, verify_team
from mod.json_module import open_json

import asyncio

async def general(bot,ctx,channel):

    author = ctx.author

    emoji_list = ["1⃣", "2⃣", "🚫"]
    embed = discord_module.default("メンバー情報登録・更新", ":one: 登録 \r\n :two: 更新 \r\n :no_entry_sign: 終了")
    msg = await channel.send(embed=embed)

    for e in emoji_list: await msg.add_reaction(e)

    r = await check_reaction(bot, channel, author, emoji_list, True)

    if r == None: return #リアクション待機エラー処理用

    user = await verify_team(bot, channel, author) #本人確認処理(戻り値:User)

    if user == None: return False #チーム確認失敗時エラー処理用

    #-------------------------
    if r == emoji_list[0]: id = key = 'all'
    elif r == emoji_list[1]:
        indiv_data = open_json('./command/menu/block/data/indiv.json')

        reactions = [i['emoji'] for i in indiv_data]
        descriptions = [f"{i['emoji']} {i['key']}" for i in indiv_data]

        option_menu = await channel.send(embed=discord_module.default("編集項目選択", '\r\n'.join(descriptions)))
        for r in reactions: await option_menu.add_reaction(r)

        reaction = await check_reaction(bot, channel, author, reactions)
        if reaction == None: return False #リアクション待機エラー処理用

        for a in indiv_data:
            if reaction == a['emoji']:
                if a['id'] == 8:
                    id = key = 'all'
                    break
                id = a['id']
                key = a['key']
                break
    #------------------------

    data = await options(bot, channel, author, user, id)

    output = await regis.post_db(data, 'indiv', key)

    if output.status_code == 200:
        await channel.send(embed=discord_module.success("正常に登録しました"))
    else:
        await channel.send(embed=discord_module.error("エラーが発生しました。"))

    await asyncio.sleep(3)


async def options(bot, channel, author, user, item):
    proc = list() #実行リスト

    if item=='all': proc = list(range(1, 7+1))
    else: proc.append(item)

    data = dict() #送信用のデータを用意

    indiv_data = open_json('./command/menu/block/data/indiv.json')
    emoji_order = open_json('./mutual/data/order.json')

    for id in proc:
        for i in indiv_data:

            if i['id'] == 4:
                data['Discord名'] = str(user)
                data['DiscordID'] = str(user.id)

            if id == i['id']:

                #メッセージで受け取り
                if i['option'] == None:
                    question = await channel.send(embed=discord_module.default('質問', i['question']))
                    answer = (await check_message(bot, channel, author)).content

                    if i['id'] == 2 and "なし" in answer: answer = '' #フレンドコード記入欄に「なし」と記載された場合

                #リアクションで受け取り
                else:
                    options = [{"emoji": r, "option": o} for (o, r) in zip(i['option'], emoji_order)]
                    reactions = [r for (o, r) in zip(i['option'], emoji_order)]
                    descriptions = [f"{r} {o}" for (o, r) in zip(i['option'], emoji_order)]

                    question = await channel.send(embed=discord_module.default('質問', i['question']+'\r\n'+'\r\n'.join(descriptions)))

                    for r in reactions: await question.add_reaction(r)

                    reaction = await check_reaction(bot, channel, author, reactions)
                    if reaction == None: return reaction #リアクション待機エラー処理用

                    for a in options:
                        if reaction == a['emoji']: 
                            answer = a['option']
                            break

                data[i['key']] = answer

    return data