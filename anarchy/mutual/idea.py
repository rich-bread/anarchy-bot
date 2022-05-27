import discord

from command.menu.block import regis
import mod.discord_module as dismod
import asyncio

#ロール一括付与
#@bot.command(aliases=['aro'])
async def add_role_at_once(ctx):
    indivList = regis.get_db("ロール一括付与")
    failed_array = []

    for i in indivList:
        ary = dismod.split_discordName(i['discordId'])

        user = discord.utils.get(ctx.guild.members, name=ary[0], discriminator=ary[1])

        if user == None:
            failed_array.append(f"名前:{i['name']} ID:{i['discordId']}")
            print(f"Couldn't add {i['league']} to {i['discordId']}.")
            continue

        leagues = ['AVG19', 'AVG20', 'AVG19&20', 
               'AVG21', 'AVG22', 'AVG21&22', 
               'AVG23', 'AVG24', 'AVG25']

        for l in leagues:
            try:
                role = discord.utils.get(ctx.guild.roles, name=l)
                await user.remove_roles(role)
            except:
                pass

        role = discord.utils.get(ctx.guild.roles, name=i['league'])

        await user.add_roles(role)
        print(f"Added {i['league']} to {i['discordId']}.")

    failed_list = '\r\n'.join(failed_array)

    error = await ctx.send(embed=dismod.error("以下の参加者にロールを付与できませんでした:\r\n"+failed_list))


#匿名質問
#@bot.command(name='ask_question', aliases=['aq'])
async def anonymous_question(ctx):
    bot = []
    if (type(ctx.channel) == discord.DMChannel) and (bot.user == ctx.channel.me):
        waiting_msg = await ctx.send(embed=dismod.waiting("質問を送信してください。待機時間300秒を超えると自動的に受付を終了します\r\n※Discordアカウント名及びIDは回収しません"))

        def check(m: discord.Message):
            return m.channel == ctx.channel and m.author.id == ctx.author.id
            
        try:
            question = await bot.wait_for('message', check=check, timeout=300)
        except asyncio.TimeoutError:
            await waiting_msg.delete()
            error = await ctx.send(embed=dismod.error("待機時間内に質問が送信されませんでした。再度コマンドを入力してください"))
            return
        else:
            await waiting_msg.delete()
            success = await ctx.send(embed=dismod.success("質問ありがとうございます。回答まで今しばらくお待ちください"))

            regis.post_db({'question': question.content}, '匿名質問')

            channel = bot.get_channel(944512330631372810)   #送信するチャンネルID
            await channel.send(question.content)

    else:
        await ctx.message.delete()
        error = await ctx.send(embed=dismod.error("匿名質問機能は**DM**でしか使えません。\r\nBOTのプロフィールからメッセージを選択し、再度コマンドを入力してください"))
        await asyncio.sleep(10)
        await error.delete()

from typing import Union
#@bot.command(name="reactiontest")
async def reaction_test(ctx): # waiting for reactions (✅, ❌) here
    bot = []
    await ctx.send(f"**{ctx.author}**, please react with :white_check_mark: or :x: on this message in 60 seconds")
    
    def check(r: discord.Reaction, u: Union[discord.Member, discord.User]):  # r = discord.Reaction, u = discord.Member or discord.User.
        return u.id == ctx.author.id and r.message.channel.id == ctx.channel.id and \
               str(r.emoji) in ["\U00002705", "\U0000274c"]
        # checking author, channel and only having the check become True when detecting a ✅ or ❌
        # else, it will timeout.

    try:
        reaction, user = await bot.wait_for(event = 'reaction_add', check = check, timeout = 60.0)
    except asyncio.TimeoutError:
        await ctx.send(f"**{ctx.author}**, you didnt react with a ✅ or ❌ in 60 seconds.")
        return
    else:
        if str(reaction.emoji) == "\U00002705":
            return await ctx.send(f"{ctx.author} reacted with a ✅")

        if str(reaction.emoji) == "\U0000274c":
            return await ctx.send(f"{ctx.author} reacted with a ❌")