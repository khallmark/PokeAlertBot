import operator
import os
import platform

import discord
import requests
import json
from pprint import pprint
from time import sleep

from cleverwrap import CleverWrap
from discord.ext import commands

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
    def __init__(self, token, cleverToken, pokedex, file_channels = []):
        super().__init__(command_prefix=["!", "?"], description="Birch", pm_help=None)
        self.token = token
        self.version = "1.1"
        self.cw = CleverWrap(cleverToken)
        self.file_channels = file_channels
        self.pokedex = pokedex

        self.add_command(self.silph)
        self.add_command(self.type)
        self.add_command(self.move)
        # self.add_command(self.compare)
        self.add_command(self.counters)
        self.add_command(self.cp)
        self.add_command(self.dex)
        self.add_command(self.moves)

        f = open("../last_updated", "r")
        self.last_updated = f.read()
        f.close()

        # self.run(self.token)

    async def on_ready(self):
        print('Logged in as '+self.user.name+' (ID:'+self.user.id+') | Connected to '+str(len(self.servers))+' servers | Connected to '+str(len(set(self.get_all_members())))+' users')
        print('--------')
        print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
        print('--------')
        print('Use this link to invite {}:'.format(self.user.name))
        print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=378944'.format(self.user.id))

        for server in self.servers:
            print ("Connected to server: {}".format(server))

    async def on_message(self, message):

        self.logMessageMeta(message)

        if self.user.id == message.author.id:
            return

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

        if (not message.author.bot) and (message.server == None or self.user in message.mentions):
            await self.send_typing(message.channel)

            txt = message.content.replace(message.server.me.mention,'') if message.server else message.content
            reply = self.cw.say(txt)

            await self.send_message(message.channel, reply)
        else:
            message.content = message.content.lower()
            await self.process_commands(message)


    @commands.command(pass_context=True)
    async def silph(self, ctx, *args):
        self.logContext(ctx)
        if len(args) != 1:
            await self.say("Command: !silph <trainer_name>")
            return

        user = args[0]

        url = "https://thesilphroad.com/{}.json".format(user)
        request = requests.get(url).json()

        if "error" in request:
            await self.say("User " + user + " not found")
            return

        silph = request["data"]

        pprint(silph)

        title = "{} ({} {}, {})".format(silph["in_game_username"], silph["trainer_level"], silph["team"], silph["title"])

        colors = {
            "Mystic" : 0x2358C2,
            "Instinct": 0xF2D044,
            "Valor": 0xA3221E,
        }

        em = discord.Embed(title=title, colour=colors[silph["team"]])

        em.set_thumbnail(url=silph["avatar"])

        home_region = silph["home_region"]
        if len(home_region) == 0:
            home_region = "No home region listed"

        description = "**Location:** {}\n**Playstyle:** {}, {}".format(home_region, silph["playstyle"], silph["goal"])

        silph_stats = "**Joined:** {}\n**Badges:** {}\n**Check-ins:** {}\n**Handshakes:** {}\n**Migrations:** {}"

        checkins = silph["checkins"]
        if "name" in checkins:
            checkins = 0
        else:
            checkins = len(checkins)

        silph_stats = silph_stats.format(silph["joined"], len(silph["badges"]), checkins, silph["handshakes"], silph["nest_migrations"])

        em.add_field(name="Silph Stats", value=silph_stats, inline=True)

        em.description = description

        em.set_footer(text="Silph Road Travelers Card - {} - Updated {}".format(silph["card_id"], silph["modified"]))

        await self.say(embed=em)


    @commands.command(pass_context=True)
    async def type(self, ctx, *args):
        """Get information about a specific type.

        Format: !type <type_name>
        Example: !type Poison
        """
        self.logContext(ctx)
        if len(args) != 1:
            await self.say("Command: !type <type_name>")
            return

        type = args[0]

        typeObj = self.pokedex.getType(type)

        if typeObj is None:
            await self.say("Type not found")
            return

        em = discord.Embed()

        em.title = typeObj.name
        em.colour = typeObj.color()

        inline = False

        effective, ineffective = self.processTypeMap(typeObj.typeIndex)

        em.add_field(name="Super Effective (140%)", value=effective, inline=inline)
        em.add_field(name="Not Very Effective (71.4%)", value=ineffective, inline=inline)

        effective, ineffective = self.processTypeMap(typeObj.defenseTypeIndex)

        em.add_field(name="Strong Against", value=ineffective, inline=inline)
        em.add_field(name="Weak Against", value=effective, inline=inline)

        em.set_thumbnail(url=typeObj.icon())

        em.set_footer(text=self.footerString())
        await self.say(embed=em)

    @commands.command(pass_context=True)
    async def move(self,ctx, *args):
        """Get information about a specific move.

        Format: !move <move_name>
        Example: !move Surf
        """
        self.logContext(ctx)
        if len(args) < 1:
            await self.say("Command: !move <move_name>")
            return

        separator = " "
        moveId = separator.join(args)
        move = self.pokedex.getMove(moveId)

        if move is None:
            await self.say("Move not found")
            return

        title = "{} ({} Type)".format(move.name, move.type.name)

        em = discord.Embed(title=title, colour=move.type.color())

        em.set_thumbnail(url=move.type.icon())

        inline = False
        effective, ineffective = self.processTypeMap(move.type.typeIndex)

        em.add_field(name="Super Effective (140%)", value=effective, inline=inline)
        em.add_field(name="Not Very Effective (71.4%)", value=ineffective, inline=inline)

        dps = "{} ({}/{})".format(move.power, move.dps(), move.dpe())
        em.add_field(name="Power (DPS/DPE)", value=dps, inline=inline)

        typeField = "Type (# Bars)"
        type = "Charge ({})".format(move.steps())
        if move.energyDelta > 0:
            typeField = "Type"
            type = "Quick"

        em.add_field(name=typeField, value=type, inline=inline)

        duration = "{}ms ({}ms - {}ms)".format(move.durationMS, move.damageWindowStart, move.damageWindowEnd)
        em.add_field(name="Duration (Dodge Window)", value=duration, inline=inline)

        em.set_footer(text=self.footerString())

        await self.say(embed=em)

    @commands.command(pass_context=True)
    async def compare(self,ctx, *args):
        self.logContext(ctx)
        if len(args) != 2:
            await self.say("Command: !compare <pokemon_name> <pokemon_name>")
            return

    @commands.command(pass_context=True)
    async def counters(self,ctx, *args):
        """Get type strengths/weaknesses for a pokemon.

        Format: !counters <pokemon_name>
        Example: !counters Rayquaza
        """
        self.logContext(ctx)
        if len(args) != 1:
            await self.say("Command: !counters <pokemon_name>")
            return

        pokemon_name = args[0]
        pokemon = self.pokedex.getPokemon(pokemon_name)

        if pokemon is None:
            await self.say("Pokemon {} not found".format(pokemon_name))
            return

        inline = True
        em = self.embedForPokemon(pokemon)

        combinedTypeMap = pokemon.type.defenseTypeIndex

        if pokemon.type2 is not None:
            for name, value in pokemon.type2.defenseTypeIndex.items():
                combinedTypeMap[name] = round(combinedTypeMap[name] * value, 3)

        effective, ineffective = self.processTypeMap(combinedTypeMap)

        em.add_field(name="Type", value=pokemon.typeString(), inline=False)
        em.add_field(name="Super Effective (140%)", value=effective, inline=inline)
        em.add_field(name="Not Very Effective (71.4%)", value=ineffective, inline=inline)

        # em.add_field(name="CP / Att / Def / HP", value="{} / {} / {} / {}".format(cp, attack, defense, hp))

        await self.say(embed=em)

    @commands.command(pass_context=True)
    async def cp(self,ctx, *args):
        """Get CP for 100 IV at the specified level.

        Format: !cp <pokemon_name> <level>
        Example: !cp Pikachu 40
        """
        self.logContext(ctx)
        if len(args) != 2 and len(args) != 5:
            await self.say("Command: !cp <pokemon_name> <level> [<atk> <def> <sta>] (bracket arguments are optional)")
            return

        pokemon = args[0]
        level = args[1]

        pokemonObj = self.pokedex.getPokemon(pokemon)

        if pokemonObj is None:
            await self.say("Pokemon not found")
            return

        if len(args) == 5:
            attack  = int(args[2])
            defense = int(args[3])
            stamina = int(args[4])
        else:
            attack = 15
            defense = 15
            stamina = 15

        cp = pokemonObj.cp(level, attack, defense, stamina)
        attack = pokemonObj.attack(level, attack)
        defense = pokemonObj.defense(level, defense)
        hp = pokemonObj.hp(level, stamina)

        em = self.embedForPokemon(pokemonObj)

        em.add_field(name="CP / Att / Def / HP", value="{} / {} / {} / {}".format(cp, attack, defense, hp))

        await self.say(embed=em)

    @commands.command(pass_context=True)
    async def dex(self,ctx, *args):
        """Get general information about a Pokémon

        Format: !dex <pokemon_name>
        Example: !dex Bulbasaur
        """
        self.logContext(ctx)
        if len(args) != 1:
            await self.say("Command: !dex <pokemon_name>")
            return

        pokemon = args[0]

        pokemonObj = self.pokedex.getPokemon(pokemon)

        if pokemonObj is None:
            await self.say("Pokemon not found")
            return

        em = self.embedForPokemon(pokemonObj)

        em.description = pokemonObj.description
        em.add_field(name="Weight / Height", value=pokemonObj.sizeString())
        em.add_field(name="Type", value=pokemonObj.typeString())
        em.add_field(name="Base Att / Def / Sta", value=pokemonObj.statString())
        em.add_field(name="Raid Boss CP (20/25)", value=pokemonObj.raidCPString([20, 25]))

        if pokemonObj.gender is not None:
            gender = "{}% / {}%".format(pokemonObj.gender.male*100, pokemonObj.gender.female*100)
            em.add_field(name="Male(%) / Female(%)", value=gender)
        else:
            em.add_field(name="Male(%) / Female(%)", value="No Gender")

        if pokemonObj.source == "game_master":
            em.add_field(name="Catch/Flee Rate", value="{}%/{}%".format(round(pokemonObj.baseCatchRate*100,1), round(pokemonObj.baseFleeRate*100,1)))

        if len(pokemonObj.varieties):
            em.add_field(name="Varieties", value="\n".join(pokemonObj.varieties))

        await self.say(embed=em)

    @commands.command(pass_context=True)
    async def moves(self,ctx, *args):
        """Gets the moves for a Pokémon
        
        Format: !moves <pokemon_name>
        Example: !moves mewtwo
        """
        self.logContext(ctx)
        if len(args) != 1:
            await self.say("Command: !moves <pokemon_name>")
            return

        pokemon = args[0]

        pokemonObj = self.pokedex.getPokemon(pokemon)

        if pokemonObj is None:
            await self.say("Pokemon not found")
            return

        em = self.embedForPokemon(pokemonObj)

        em.add_field(name="Quick Moves", value=self.generateMoveString(pokemonObj.quickMoves, pokemonObj.stabMoves, pokemonObj.legacyMoves), inline=False)
        em.add_field(name="Charge Moves", value=self.generateMoveString(pokemonObj.chargeMoves, pokemonObj.stabMoves, pokemonObj.legacyMoves), inline=False)

        await self.say(embed=em)

    # Processes a list of [TYPE_ID] => scalar for output
    def processTypeMap(self, typeIndex, separator=", "):
        ineffectiveMoves = []
        effectiveMoves = []

        for typeName, typeScalar in sorted(typeIndex.items(), key=operator.itemgetter(1), reverse=True):
            # Assuming the type exists because it should
            theType = Type.objects(templateId__iexact=typeName)[0]
            if typeScalar > 1.4:
                effectiveMoves.append("{} ({}%)".format(theType.name, round(typeScalar*100, 2)))
            elif typeScalar > 1:
                effectiveMoves.append(theType.name)
            elif typeScalar < .714:
                ineffectiveMoves.append("{} ({}%)".format(theType.name, round(typeScalar*100, 2)))
            elif typeScalar < 1:
                ineffectiveMoves.append(theType.name)

        effective = "No Effective Moves"
        if len(effectiveMoves):
            effective = separator.join(effectiveMoves)

        ineffective = "No Ineffective Moves"
        if len(ineffectiveMoves):
            ineffective = separator.join(ineffectiveMoves)

        return (effective, ineffective)

    # Generates the embed for a Pokemon related command (!cp, !dex, !moves)
    def embedForPokemon(self, pokemonObj):
        title = pokemonObj.name

        if pokemonObj.category is not None:
            title = "#{} {} ({} Pokémon, Gen {})".format(pokemonObj.number, pokemonObj.name, pokemonObj.category, pokemonObj.generationStr())
        else:
            title = "#{} {} (Gen {})".format(pokemonObj.number, pokemonObj.name, pokemonObj.generationStr())

        em = discord.Embed(title=title, colour=pokemonObj.type.color())

        tn = pokemonObj.icon()
        em.set_thumbnail(url=tn)

        em.set_footer(text=self.footerString(pokemonObj))

        return em

    def footerString(self, pokemonObj=None):
        footer = "Data is accurate for Pokémon Go."
        if pokemonObj is not None and pokemonObj.source == "pokeapi":
            footer="Data was loaded from pokeapi.co and may change before release."

        footer = footer + " Bot Version " + self.version + ". Data Updated: " + self.last_updated

        return footer

    # Generates a move string for the !moves command
    def generateMoveString(self, moves: [Move], stabMoves: [Move], legacyMoves: [Move]):
        if len(moves) == 0:
            return "No Moves Found"

        moveStrings = []
        for move in moves:
            stabStr = ""
            if move in stabMoves:
                stabStr = ", STAB"

            legacyStr = ""
            if move in legacyMoves:
                legacyStr = ", Legacy"

            if move.charge == True:
                moveStrings.append(
                    "{} ({} DPS, {} DPE, {}{}{})".format(
                        move.name,
                        move.dps(stabMoves=stabMoves, weather=None),
                        move.dpe(stabMoves=stabMoves, weather=None),
                        move.type.name,
                        stabStr,
                        legacyStr
                    )
                )
            else:
                moveStrings.append(
                    "{} ({} DPS, {}{}{})".format(
                        move.name,
                        move.dps(stabMoves=stabMoves, weather=None),
                        move.type.name,
                        stabStr,
                        legacyStr
                    )
                )

        newLineString = "\n"

        return newLineString.join(moveStrings)

    # Adds a channel to grab files from
    def addFileChannel(self, channelId):
        self.file_channels.append(channelId)

    def logMessageMeta(self, message):
        if (message.author.bot) or (self.user.id == message.author.id):
            return

        log = MessageLog()

        log.chanId = "{}-{}".format(message.server, message.channel)
        log.user = str(message.author)
        log.channel = str(message.channel)
        log.server = str(message.server)
        log.length = len(message.content)

        log.save()

    def logContext(self, ctx):
        log = CommandLog()

        log.user = str(ctx.message.author)
        log.channel = str(ctx.message.channel)
        log.server = str(ctx.message.server)
        log.command = ctx.invoked_with
        log.message = ctx.message.content

        log.save()
