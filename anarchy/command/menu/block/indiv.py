import discord

from mod.json_module import open_json
import mod.discord_module as dismod

from command.menu.block import regis
from command.menu.block.menu_common import await_message, await_reaction, verify_team, presence_userdata


async def general(bot, channel, author):

    try:
        pass
    except Exception as e:
        pass
        

    menu_data = open_json('./command/menu/menu.json')
    emoji_list = [i['emoji']  for i in menu_data[0]['option']]
    title = menu_data[0]['name']
    descriptions = '\r\n'.join([f"{i['emoji']} {i['name']}" for i in menu_data[0]['option']])

    r = await await_reaction(bot, channel, author, emoji_list, title, descriptions, True)
    if r == None: return #リアクション待機エラー処理用

    #変更対象確認処理
    user = await verify_team(bot, channel, author)
    if user == None: return #チーム確認失敗時エラー処理用

    #-------------------------
    #「登録」の場合
    if r == emoji_list[0]: id = key = 'all'

    #「更新」の場合
    elif r == emoji_list[1]:

        #ユーザデータがデータベースに存在するか確認
        exists = await presence_userdata(user.id)
        if exists == False:
            await channel.send(embed=dismod.error("変更対象のユーザデータがデータベース上で確認できませんでした。新規登録は選択肢「1⃣ 登録」よりお願いいたします"))
            return

        indiv_data = open_json('./command/menu/block/data/indiv.json')
        reactions = [i['emoji'] for i in indiv_data]
        descriptions = [f"{i['emoji']} {i['key']}" for i in indiv_data]

        reaction = await await_reaction(bot, channel, author, reactions, "編集項目選択", '\r\n'.join(descriptions))
        if reaction == None: return #リアクション待機エラー処理用

        for a in indiv_data:
            if reaction == a['emoji']:
                if a['id'] == 8:
                    id = key = 'all'
                    break
                id = a['id']
                key = a['key']
                break
    #------------------------

    #データ整形、データベースに登録
    data = await options(bot, channel, author, user, id)
    output = await regis.post_db(data, 'indiv', key)

    #ステータスコードより、リクエストを確認
    if output.status_code == 200:
        await channel.send(embed=dismod.success("正常に登録しました"))
        dm = await dismod.create_dm(author)
        await dm.send(embed=dismod.success(f"{user}の情報を正常に登録しました。"))
    else:
        await channel.send(embed=dismod.error("エラーが発生しました。"))


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
                    answer = (await await_message(bot, channel, author, '質問', i['question']))

                    if i['id'] == 2 and "なし" in answer: answer = '' #フレンドコード記入欄に「なし」と記載された場合

                #リアクションで受け取り
                else:
                    options = [{"emoji": r, "option": o} for (o, r) in zip(i['option'], emoji_order)]
                    reactions = [r for (o, r) in zip(i['option'], emoji_order)]
                    descriptions = [f"{r} {o}" for (o, r) in zip(i['option'], emoji_order)]

                    reaction = await await_reaction(bot, channel, author, reactions, '質問', i['question']+'\r\n'+'\r\n'.join(descriptions))

                    if reaction == None: return #リアクション待機エラー処理用

                    for a in options:
                        if reaction == a['emoji']: 
                            answer = a['option']
                            break

                data[i['key']] = answer

    return data