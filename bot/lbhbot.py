import discord
import asyncio
# from discord.ext.commands import Bot
from discord.ext import commands
import platform
import json
import requests
from cleverwrap import CleverWrap

class LBHBot(commands.Bot):
    def __init__(self, token, cleverToken):
        super().__init__(command_prefix="?", description="Birch", pm_help=None)
        self.token = token
        self.cw = CleverWrap(cleverToken)

    async def on_ready(self):
        print('Logged in as '+self.user.name+' (ID:'+self.user.id+') | Connected to '+str(len(self.servers))+' servers | Connected to '+str(len(set(self.get_all_members())))+' users')
        print('--------')
        print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
        print('--------')
        print('Use this link to invite {}:'.format(self.user.name))
        print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(self.user.id))

    async def on_message(self, message):
        if (not message.author.bot) and (message.server == None or self.user in message.mentions):
            await self.send_typing(message.channel)
            txt = message.content.replace(message.server.me.mention,'') if message.server else message.content
            reply = self.cw.say(txt)
            await self.send_message(message.channel, reply)
        else:x  x
            await self.process_commands(message)

    @commands.command()
    async def ping(self, *args):
        await self.say(":ping_pong: Pong!")
        await asyncio.sleep(3)

    @commands.command()
    async def test(self, *args):
        await self.say(":kappa:")

    def run(self):
        super().run(self.token, reconnect=True)