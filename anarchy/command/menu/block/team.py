import discord

from mod.json_module import open_json
import mod.discord_module as dismod

from command.menu.block.menu_common import check_message, check_reaction, get_user, id_fromMention, presence_userdata

from command.menu.block import regis, indiv

async def team_main(bot, ctx, channel):
    emoji_list = ["1️⃣", "2️⃣", "🚫"]
    pass


async def create_team(bot, channel, author, item, additional=True):
    proc = list() #実行リスト

    if item=='all': proc = list(range(1, 7+1))
    elif item=='continue': proc = list(range(3, 8))
    else: proc.append(item)

    data = dict()

    team = open_json('./command/menu/block/data/team.json')
    emojis = open_json('./mutual/data/order.json')

    for id in proc:
        for i in team:

            if additional != True and i['id'] == 7: continue

            if id == i['id']:
                #メッセージで受け取り
                if i['option'] == None:
                    if i['id'] == 1 or i['id'] == 2:
                        question = await channel.send(embed=dismod.default('質問', i['question']))
                        answer = await check_message(bot, channel, author)
                    else:
                        count=0
                        while count<1:
                            question = await channel.send(embed=dismod.default('質問', i['question']))
                            mention = await check_message(bot, channel, author)
                            if mention == None: return

                            if "<@" not in mention:
                                await channel.send(embed=dismod.error("正しいメンションではありません。再度入力してください"))
                                await question.delete()
                                continue
                            else:
                                id = id_fromMention(mention)
                                count+=1


                    exists = await presence_userdata(id)
                    if exists == False:
                        user = await get_user(bot, id)
                        new_member = await indiv.options(bot, channel, author, user, 'all')
                        await regis.post_db(new_member, 'indiv', 'all')

                    answer = id

                #リアクションで受け取り
                else:
                    options = [{"emoji": r, "option": o} for (o, r) in zip(i['option'], emojis)]
                    reactions = [r for (o, r) in zip(i['option'], emojis)]
                    descriptions = [f"{r} {o}" for (o, r) in zip(i['option'], emojis)]

                    question = await channel.send(embed=dismod.default('質問', i['question']+'\r\n'+'\r\n'.join(descriptions)))

                    for r in reactions: await question.add_reaction(r)

                    reaction = await check_reaction(bot, channel, author, reactions)
                    if reaction == None: return reaction #リアクション待機エラー処理用

                    for a in options:
                        if reaction == a['emoji']: 
                            answer = a['option']
                            break

                data[i['key']] = answer

    return data