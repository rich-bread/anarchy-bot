import discord
from discord.ext import commands, tasks
import requests

import mod.discord_module as dismod

class send(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #エラー
    def note_error(content):
        embed=discord.Embed(description=content,color=0xEC1A2E)
        embed.set_author(name='管理者エラー通知', icon_url='https://www.freeiconspng.com/thumbs/error-icon/error-icon-4.png')
        return embed

    async def error(self, e):
        channel_id = 985120626551443486 #エラーメッセージ送信先チャンネルID
        admin_id = 754653200757424149 #管理者アカウントID

        channel = self.bot.get_channel(channel_id)
        admin = self.bot.fetch_user(admin_id)

        await channel.send(embed=note_error(e+f"\r\n<@{admin.id}>"))