from discord.ext import commands
import discord

import asyncio
import aiohttp

import os

import asyncio
import platform
import json
import requests
from cleverwrap import CleverWrap

class LBHImageDownload:
    def __init__(self, url, filename):
        self.url = url
        self.filename = filename

    # get content and write it to file
    def write_to_file(self, content):
        f = open(self.filename, 'wb')
        f.write(content)
        f.close()


class LBHBot(commands.Bot):
    def __init__(self, token, cleverToken):
        super().__init__(command_prefix=["?", "!"], description="Birch", pm_help=None)
        self.token = token
        self.cw = CleverWrap(cleverToken)
        self.file_channels = []

        # avoid to many requests(coroutines) the same time.
        # limit them by setting semaphores (simultaneous requests)
        self.r_semaphore = asyncio.Semaphore(10)

        self.add_command(self.test)
        self.add_command(self.ping)

    async def on_ready(self):
        print('Logged in as '+self.user.name+' (ID:'+self.user.id+') | Connected to '+str(len(self.servers))+' servers | Connected to '+str(len(set(self.get_all_members())))+' users')
        print('--------')
        print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
        print('--------')
        print('Use this link to invite {}:'.format(self.user.name))
        print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(self.user.id))

    async def on_message(self, message):
        if (message.channel.id in self.file_channels) and len(message.attachments) > 0:
            save_path = "files/"+message.server.name+"/"+message.author.display_name+"/"

            images = []
            for attachment in message.attachments:
                url = attachment.get("url")
                extension = os.path.splitext(attachment.get("filename"))
                filepath = save_path+message.timestamp.strftime("%d-%m-%y-%H-%m-%S")+extension[0]+extension[1]
                images.append(LBHImageDownload(url, filepath))


            coroutines = [self.save_file(image, message) for image in images]
            eloop = asyncio.get_event_loop()
            eloop.run_until_complete(asyncio.wait(coroutines))
            eloop.close()

        if (not message.author.bot) and (message.server == None or self.user in message.mentions):
            await self.send_typing(message.channel)
            txt = message.content.replace(message.server.me.mention,'') if message.server else message.content
            reply = self.cw.say(txt)
            await self.send_message(message.channel, reply)
        else:
            await self.process_commands(message)

    # a helper coroutine to perform GET requests:
    @asyncio.coroutine
    def get(self, *args, **kwargs):
        response = yield from aiohttp.request('GET', *args, **kwargs)
        return (yield from response.read_and_close())

    @asyncio.coroutine
    def save_file(self, image, message):
        # this routine is protected by a semaphore
        with (yield from self.r_semaphore):
            content = yield from asyncio.async(self.get(image.url))
            image.write_to_file(content)
            yield self.add_reaction(message, u"\U0001F44D")

    @commands.command()
    async def ping(self, *args):
        await self.say(":ping_pong: Pong!")
        await asyncio.sleep(3)

    @commands.command()
    async def test(self, *args):
        await self.say(":kappa:")
