import os
import platform
import sys

from discord.ext import commands
import discord
import requests
from cleverwrap import CleverWrap

from pokelib.documents import *

class LBHImageDownload:
    def __init__(self, url, filename):
        self.url = url
        self.filename = filename

    def save_file(self):
        response = requests.get(self.url)
        self.write_to_file(response.content)

    def write_to_file(self, content):
        dirname = os.path.dirname(self.filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        f = open(self.filename, 'wb')
        f.write(content)
        f.close()


class LBHBot(commands.Bot):
    def __init__(self, token, cleverToken, pokedex):
        super().__init__(command_prefix=["?", "!"], description="Birch", pm_help=None)
        self.token = token
        self.cw = CleverWrap(cleverToken)
        self.file_channels = []
        self.pokedex = pokedex

        self.add_command(self.dex)
        self.add_command(self.cp)
        self.add_command(self.moves)

        self.run(self.token)

    # Adds a channel to grab files from
    def addFileChannel(self, channelId):
        self.file_channels.append(channelId)

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
                filepath = save_path+message.timestamp.strftime("%d-%m-%y-%H-%m-%S")+"-" + extension[0]+extension[1]
                images.append(LBHImageDownload(url, filepath))


            for image in images:
                image.save_file()
                await self.add_reaction(message, u"\U0001F44D")

        if (not message.author.bot) and (message.server == None or self.user in message.mentions) and not (self.user.id == message.author.id):
            await self.send_typing(message.channel)
            txt = message.content.replace(message.server.me.mention,'') if message.server else message.content
            reply = self.cw.say(txt)
            await self.send_message(message.channel, reply)
        else:
            await self.process_commands(message)

    @commands.command()
    async def cp(self, *args):
        if len(args) != 2:
            await self.say("Command: ?cp <pokemon_name> <level>")
            return

        pokemon = args[0]
        level = args[1]

        pokemonObj = self.pokedex.getPokemon(pokemon)

        if pokemonObj is None:
            await self.say("Pokemon not found")
            return

        cp = pokemonObj.cp(level, 15, 15, 15)

        await self.say(pokemonObj.name + " 100% CP @ level " + str(level) + ": " + str(cp))

    @commands.command()
    async def dex(self, *args):

        if len(args) != 1:
            await self.say("Command: ?dex <pokemon_name>")
            return

        pokemon = args[0]

        pokemonObj = self.pokedex.getPokemon(pokemon)

        if pokemonObj is None:
            await self.say("Pokemon not found")
            return

        # title = pokemonObj.name
        #
        # if pokemonObj.category is not None:
        #     title = pokemonObj.name + " (" + pokemonObj.category + " Pokémon)"
        #
        # em = discord.Embed(title=title, description=pokemonObj.description, colour=0xDEADBF)
        #

        #
        # tn = pokemonObj.icon()
        # em.set_thumbnail(url=tn)

        em = self.embedForPokemon(pokemonObj)

        typeString = pokemonObj.type.name

        if pokemonObj.type2 is not None:
            typeString = typeString+"/"+pokemonObj.type2.name

        em.add_field(name="Type", value=typeString, inline=True)

        em.add_field(name="Base Attack", value=pokemonObj.baseAttack, inline=True)
        em.add_field(name="Base Defense", value=pokemonObj.baseDefense, inline=True)
        em.add_field(name="Base Stamina", value=pokemonObj.baseStamina, inline=True)

        em.add_field(name="100% Level 20 CP", value=pokemonObj.cp(20, 15, 15, 15), inline=True)
        em.add_field(name="100% Level 25 CP", value=pokemonObj.cp(25, 15, 15, 15), inline=True)

        # em.set_author(name='Someone', icon_url=client.user.default_avatar_url)

        await self.say(embed=em)

    def embedForPokemon(self, pokemonObj):
        title = pokemonObj.name

        if pokemonObj.category is not None:
            title = pokemonObj.name + " (" + pokemonObj.category + " Pokémon)"

        em = discord.Embed(title=title, description=pokemonObj.description, colour=0xDEADBF)

        tn = pokemonObj.icon()
        em.set_thumbnail(url=tn)

        return em


    @commands.command()
    async def moves(self, *args):
        if len(args) != 1:
            await self.say("Command: ?dex <pokemon_name>")
            return

        pokemon = args[0]

        pokemonObj = self.pokedex.getPokemon(pokemon)

        if pokemonObj is None:
            await self.say("Pokemon not found")
            return

        em = self.embedForPokemon(pokemonObj)
        quickMoves = pokemonObj.quickMoves

        quickString = ""
        for move in quickMoves:
            quickString += self.generateMoveString(pokemonObj, move)

        em.add_field(name="Quick Moves", value=quickString, inline=False)

        chargeString = ""
        for move in pokemonObj.chargeMoves:
            chargeString += self.generateMoveString(pokemonObj, move)

        em.add_field(name="Charge Moves", value=chargeString, inline=False)

        await self.say(embed=em)

    def generateMoveString(self, pokemonObj: Pokemon, move: Move):
        stabStr = ""
        if move in pokemonObj.stabMoves:
            stabStr = ", STAB"

        return move.name + " (" + str(move.dps(pokemon=pokemonObj, weather=None)) + " DPS, " + move.type.name + "" + stabStr + ")\n"

