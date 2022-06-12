import discord

from command.menu.block import regis, team
import mod.discord_module as dismod

from mod.json_module import open_json

from command.menu.block.menu_common import check_message, check_reaction, await_message, await_reaction

async def continued_participation(bot, ctx, channel):

    author = ctx.author

    #いずれかのチームリーダーかどうか確認
    teamdata = (await regis.verify_leader('check-leader', author.id)).json()
    if teamdata == None: 
        await channel.send(embed=dismod.error("いずれかのチームのリーダーであることが確認できませんでした。\r\nチームリーダーであるにもかかわらず、"\
                                                                +"このエラーメッセージが送信された場合は <@754653200757424149> までご連絡ください"))
        return

    await channel.send(embed=dismod.waiting("現在チーム情報を収集しています、今しばらくお待ちください"))

    #チーム情報を貼り付け、確認を取る
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
    yon_reactions = [i['emoji'] for i in yon]
    yon_descriptions = [f"{i['emoji']} {i['content']}" for i in yon]

    team_check = await channel.send(embed=dismod.default("チーム確認", \
                                        "このチームでよろしいですか？\r\n" + '\r\n'.join(yon_descriptions)))
    for r in yon_reactions: await team_check.add_reaction(r)

    reaction = await check_reaction(bot, channel, author, yon_reactions)
    if reaction == None: return

    if reaction == yon_reactions[1]: #「いいえ」選択
        await channel.send(embed=dismod.error("継続受付プログラムを終了します。違うチームが表示された場合は <@754653200757424149> までご連絡ください"))
        return

    #リーグ変更の有無を確認
    league_change = await await_reaction(bot, channel, author, yon_reactions, "リーグ変更", "リーグの変更はありますか？")

    if league_change == yon_reactions[0]:
        team_data = open_json('./command/menu/block/data/team.json')
        emoji_order = open_json('./mutual/data/order.json')

        for i in team_data:

            if i['id'] != 2: continue

            options = [{"emoji": r, "option": o} for (o, r) in zip(i['option'], emoji_order)]
            reactions = [r for (o, r) in zip(i['option'], emoji_order)]
            descriptions = [f"{r} {o}" for (o, r) in zip(i['option'], emoji_order)]

            reaction = await await_reaction(bot, channel, author, reactions, '質問', i['question']+'\r\n'+'\r\n'.join(descriptions))
            if reaction == None: return reaction #リアクション待機エラー処理用

            for a in options:
                if reaction == a['emoji']: 
                    league = a['option']
                    break
    else: league = teamdata[3]

    
    #メンバー変更の有無を確認
    member_change = await channel.send(embed=dismod.default("メンバー変更", "メンバーの変更はありますか？"))
    for r in yon_reactions: await member_change.add_reaction(r)

    reaction = await check_reaction(bot, channel, author, yon_reactions)
    if reaction == None: return

    if reaction == yon_reactions[0]:

        member_addition = await channel.send(embed=dismod.default("メンバー人数", "5人目のメンバー追加はありますか？"))
        for r in yon_reactions: await member_addition.add_reaction(r)

        reaction = await check_reaction(bot, channel, author, yon_reactions)
        if reaction == None: return

        if reaction == yon_reactions[0]: additional = True
        else: additional = False

        data = {"チーム名": teamdata[1], "チームID": teamdata[2], "リーグ": league}
        try:
            data.update(await team.create_team(bot, channel, author, 'continue', additional))
        except: pass
    else:
        data = {"チーム名": teamdata[1], "チームID": teamdata[2], "リーグ": league, 
                "リーダーID": teamdata[4], "メンバー[2]ID": teamdata[5],
                "メンバー[3]ID": teamdata[6], "メンバー[4]ID": teamdata[7]}

        if len(teamdata) == 9: data.update({"メンバー[5]ID": teamdata[8]})

    output = await regis.post_db(data, 'team', 'all')

    if output.status_code == 200:
        await channel.send(embed=dismod.success("正常に登録しました"))

        dm = await dismod.create_dm(author)
        await dm.send(embed=dismod.success(f"**{teamdata[1]}** の継続受付を完了しました。来シーズンも**BOMU☆LEAGUE-Anarchy-**をよろしくお願いいたします"))

    else:
        await channel.send(embed=dismod.error("エラーが発生しました"))