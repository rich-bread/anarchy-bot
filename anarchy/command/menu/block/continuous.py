import discord

from command.menu.block import regis, team
import mod.discord_module as dismod

from mod.json_module import open_json

from command.menu.block.menu_common import check_message, check_reaction

async def continued_participation(bot, ctx, channel):

    author = ctx.author

    #------------いずれかのチームリーダーかどうか確認------------
    teamdata = (await regis.verify_leader('check-leader', author.id)).json()

    if teamdata == None: 
        await channel.send(embed=dismod.error("いずれかのチームのリーダーであることが確認できませんでした。\r\nチームリーダーであるにもかかわらず、"\
                                                                +"このエラーメッセージが送信された場合は <@754653200757424149> までご連絡ください"))
        return

    print(teamdata)
    #-----------チーム情報を貼り付け、確認を取る----------------
    teaminfo = f"チーム名: {teamdata[1]}\r\nリーグ: {teamdata[3]}"

    memberid = []
    count = 4
    while count < 9:
        if teamdata[count] == '': pass
        else: memberid.append(teamdata[count])
        count+=1

    memberdata = []
    for id in memberid:
        member = (await regis.get_db('read', 'indiv', id, 'all')).json()
        memberdata.append(member[1])

    await channel.send(embed=dismod.default("チーム詳細", teaminfo + "\r\nメンバー:" + " ".join(memberdata)))

    yon = open_json('./mutual/data/yon.json')
    reactions = [i['emoji'] for i in yon]
    descriptions = [f"{i['emoji']} {i['content']}" for i in yon]

    team_check = await channel.send(embed=dismod.default("チーム確認", \
                                        "このチームでよろしいですか？\r\n" + '\r\n'.join(descriptions)))
    for r in reactions: await team_check.add_reaction(r)

    reaction = await check_reaction(bot, channel, author, reactions)
    if reaction == None: return

    if reaction == reactions[1]: 
        await channel.send(embed=dismod.error("継続受付プログラムを終了します。違うチームが表示された場合は <@754653200757424149> までご連絡ください"))
        return
    
    #メンバー変更の有無を確認
    member_change = await channel.send(embed=dismod.default("メンバー変更", "メンバーの変更はありますか？"))
    for r in reactions: await member_change.add_reaction(r)

    reaction = await check_reaction(bot, channel, author, reactions)
    if reaction == None: return

    if reaction == reactions[0]:

        member_addition = await channel.send(embed=dismod.default("メンバー人数", "5人目のメンバー追加はありますか？"))
        for r in reactions: await member_addition.add_reaction(r)

        reaction = await check_reaction(bot, channel, author, reactions)
        if reaction == None: return

        if reaction == reaction[0]: additional = True
        else: additional = False

        data = {"チーム名": teamdata[1], "チームID": teamdata[2], "リーグ": teamdata[3]}
        data.update(await team.create_team(bot, channel, author, 'continue', additional))
    else:
        data = {"チーム名": teamdata[1], "チームID": teamdata[2], "リーグ": teamdata[3], 
                "リーダーID": teamdata[4], "メンバー[2]ID": teamdata[5],
                "メンバー[3]ID": teamdata[6], "メンバー[4]ID": teamdata[7]}

        if len(teamdata) == 9: data.update({"メンバー[5]ID": teamdata[8]})

    output = await regis.post_db(data, 'team', 'all')

    if output.status_code == 200:
        await channel.send(embed=dismod.success("正常に登録しました"))
    else:
        await channel.send(embed=dismod.error("エラーが発生しました。"))