from pokelib.documents import *
from lxml import html
from time import sleep
import requests
import pokebase
import os
from pprint import pprint

class PokedexImport:
    def createMap(self, objectType):
        objects = objectType.objects
        map = {}

        for object in objects:
            map[object.templateId] = object
        return map


    def importTypes(self, typeData):
        dbMap = self.createMap(Type)

        for type in typeData:
            typeObj = False

            templateId = type['templateId']
            name = templateId.split("_")[2].capitalize()

            if templateId in dbMap:
                typeObj = dbMap[templateId]
            else:
                typeObj = Type()

                typeObj.templateId = templateId
                typeObj.name = name

            dbMap[templateId] = typeObj

        for type in typeData:
            templateId = type['templateId']
            name = templateId.split("_")[2].capitalize()

            if templateId in dbMap:
                typeObj = dbMap[templateId]

            attackScalars = type["typeEffective"]["attackScalar"]

            for index, scalar in enumerate(attackScalars):
                type_name = Type.type_order[index]

                typeObj.typeIndex[type_name] = scalar

                dbMap[type_name].setDefenseType(templateId, scalar)

        for item in dbMap:
            dbMap[item].save()

        return dbMap

    def importWeather(self, weatherData, types):

        dbMap = self.createMap(Weather)
        weatherMap = {}

        for weather in weatherData:
            templateId = weather["templateId"]

            weatherAffinities = weather["weatherAffinities"]
            name = weatherAffinities["weatherCondition"].capitalize()

            weatherObj = 0
            if templateId in dbMap:
                weatherObj = dbMap[templateId]

                weatherObj.name = name
                weatherObj.templateId = templateId
            else:
                weatherObj = Weather(
                    templateId = templateId,
                    name = name
                )

                for pType in weatherAffinities["pokemonType"]:
                    if pType in types:
                        weatherObj.typeBoost.append(types[pType])

                dbMap[templateId] = weatherObj

            weatherObj.save()

        return dbMap

    def importMoves(self, moveData, types):
        dbMap = self.createMap(Move)

        for move in moveData:
            moveObj = False

            templateId = move["templateId"][11:].replace("_FAST", "")


            name = templateId.replace("_", " ").title()


            if templateId in dbMap:
                moveObj = dbMap[templateId]
            else:
                moveObj = Move(
                    templateId = templateId,
                    name = name
                )

            moveObj.name = name
            moveSettings = move["moveSettings"]

            charge = True
            if "_FAST" in move["templateId"]:
                charge = False

            moveObj.charge = charge

            if moveSettings["pokemonType"] in types:
                moveObj.type = types[moveSettings['pokemonType']]

            moveObj.durationMS = moveSettings["durationMs"]

            if "energyDelta" in moveSettings:
                moveObj.energyDelta = moveSettings["energyDelta"]
            # else:
            #     print(name)


            if "staminaLossScalar" in moveSettings:
                moveObj.staminaLossScalar = moveSettings["staminaLossScalar"]

            moveObj.damageWindowStart = moveSettings["damageWindowStartMs"]
            moveObj.damageWindowEnd   = moveSettings["damageWindowEndMs"]


            if "power" in moveSettings:
                moveObj.power = moveSettings["power"]
            else:
                moveObj.power = 0

            moveObj.save()

            dbMap[templateId] = moveObj

        return dbMap

    def importPokemon(self, pokemonData, spawns, types, weather, moves):
        dbMap = self.createMap(Pokemon)

        for pokemon in pokemonData:
            pokemonObj = False

            templateId = pokemon["templateId"]

            pokemonNumber = int(templateId.split("_")[0][1:])

            pokemonSettings = pokemon["pokemonSettings"]

            species = pokemonSettings["pokemonId"].title().replace("_", "-")
            if "form" in pokemonSettings:
                name = pokemonSettings["form"].title().replace("_", "-")
            else:
                name = species

            if templateId in dbMap:
                pokemonObj = dbMap[templateId]
            else:
                pokemonObj = Pokemon(
                    templateId = templateId,
                    name = name
                )

            pokemonObj.source = "game_master"

            pokemonObj.name = name
            pokemonObj.species = species

            pokemonObj.number = pokemonNumber
            pokemonObj.generation = self.generation(pokemonNumber)
            pokemonObj.type = types[pokemonSettings["type"]]

            if "type2" in pokemonSettings:
                pokemonObj.type2 = types[pokemonSettings["type2"]]

            pokemonObj.baseAttack  = pokemonSettings['stats']['baseAttack']
            pokemonObj.baseDefense = pokemonSettings['stats']['baseDefense']
            pokemonObj.baseStamina = pokemonSettings['stats']['baseStamina']

            pokemonObj.weight = pokemonSettings['pokedexWeightKg']
            pokemonObj.height = pokemonSettings['pokedexHeightM']

            encounter = pokemonSettings['encounter']

            if "baseCaptureRate" in encounter:
                pokemonObj.baseCatchRate = round(encounter['baseCaptureRate'], 2)

                if pokemonObj.baseCatchRate > 1:
                    print("Large Capture Rate: " + pokemonObj.name)
                    pokemonObj.baseCatchRate = round(pokemonObj.baseCatchRate / 100, 2)
            else:
                print("No Capture Rate: " + pokemonObj.name)
                pokemonObj.baseCatchRate = 0.0

            if "baseFleeRate" in encounter:
                pokemonObj.baseFleeRate = round(encounter['baseFleeRate'],2)

                if pokemonObj.baseFleeRate > 1:
                    print("Large Flee Rate: " + pokemonObj.name)
                    pokemonObj.baseFleeRate = round(pokemonObj.baseFleeRate / 100, 2)
            else:
                print("No Flee Rate: " + pokemonObj.name)
                pokemonObj.baseFleeRate = 0.0

            if pokemonNumber != 235:
                stabMoves = []
                legacyMoves = []

                quickMoves = []
                for quickMove in pokemonSettings["quickMoves"]:
                    moveId = quickMove.replace("_FAST", "")
                    if moveId in moves:
                        move = moves[moveId]

                        if move not in quickMoves:
                            quickMoves.append(move)
                            if move.type == pokemonObj.type or (pokemonObj.type2 is not None and move.type == pokemonObj.type2):
                                stabMoves.append(move)


                chargeMoves = []
                for chargeMove in pokemonSettings["cinematicMoves"]:
                    if chargeMove in moves and chargeMove not in chargeMoves:
                        move = moves[chargeMove]

                        if move not in chargeMoves:
                            chargeMoves.append(move)
                            if move.type == pokemonObj.type or (pokemonObj.type2 is not None and move.type == pokemonObj.type2):
                                stabMoves.append(move)


                pokemonObj.quickMoves = quickMoves
                pokemonObj.chargeMoves = chargeMoves
                pokemonObj.stabMoves = stabMoves
                pokemonObj.legacyMoves = legacyMoves

            pokemonObj.save()
            dbMap[templateId] = pokemonObj

        return dbMap

    def generation(self, number):

        generation = 1
        if number <= 151:
            generation = 1
        elif number <= 251:
            generation = 2
        elif number <= 386:
            generation = 3
        elif number <= 493:
            generation = 4
        elif number <= 649:
            generation = 5
        elif number <= 721:
            generation = 6
        elif number <= 807:
            generation = 7
        else:
            generation = 8

        return generation


    def addLegacyMove(self, pokemonName, moveName):
        results = Pokemon.objects(name__iexact=pokemonName)

        if len(results) == 0:
            return

        pokemon = results[0]

        results = Move.objects(name__iexact=moveName)

        if len(results) == 0:
            return

        move = results[0]

        if move not in pokemon.legacyMoves:
            pokemon.legacyMoves.append(move)

        if move.charge and move not in pokemon.chargeMoves:
            pokemon.chargeMoves.append(move)
        elif move not in pokemon.quickMoves:
            pokemon.quickMoves.append(move)

        if move not in pokemon.stabMoves and move.type == pokemon.type or (pokemon.type2 is not None and move.type == pokemon.type2):
            pokemon.stabMoves.append(move)

        pokemon.save()

    def addLegacyMoves(self):
        self.addLegacyMove("Alakazam", "Dazzling Gleam")
        self.addLegacyMove("Alakazam", "Psychic")
        self.addLegacyMove("Arcanine", "Bite")
        self.addLegacyMove("Arcanine", "Bulldoze")
        self.addLegacyMove("Arcanine", "Flamethrower")
        self.addLegacyMove("Articuno", "Hurricane")
        self.addLegacyMove("Beedril", "Bug Bite")
        self.addLegacyMove("Blaziken", "Stone Edge")
        self.addLegacyMove("Breloom", "Grass Knot")
        self.addLegacyMove("Butterfree", "Bug Bite")
        self.addLegacyMove("Chansey", "Psybeam")
        self.addLegacyMove("Charizard", "Ember")
        self.addLegacyMove("Charizard", "Wing Attack")
        self.addLegacyMove("Charizard", "Flamethrower")
        self.addLegacyMove("Charmeleon", "Scratch")
        self.addLegacyMove("Clefable", "Pound")
        self.addLegacyMove("Cleffa", "Psychic")
        self.addLegacyMove("Cleffa", "Body Slam")
        self.addLegacyMove("Cloyster", "Blizzard")
        self.addLegacyMove("Cloyster", "Icy Wind")
        self.addLegacyMove("Delibird", "Ice Shard")
        self.addLegacyMove("Delibird", "Quick Attack")
        self.addLegacyMove("Dewgong", "Ice Shard")
        self.addLegacyMove("Dewgong", "Aqua Jet")
        self.addLegacyMove("Dewgong", "Icy Wind")
        self.addLegacyMove("Diglett", "Mud Shot")
        self.addLegacyMove("Dodrio", "Air Cutter")
        self.addLegacyMove("Doduo", "Swift")
        self.addLegacyMove("Dragonite", "Dragon Breath")
        self.addLegacyMove("Dragonite", "Dragon Claw")
        self.addLegacyMove("Dragonite", "Dragon Pulse")
        self.addLegacyMove("Dugtrio", "Mud Shot")
        self.addLegacyMove("Eevee", "Body Slam")
        self.addLegacyMove("Ekans", "Gunk Shot")
        self.addLegacyMove("Electrode", "Tackle")
        self.addLegacyMove("Elekid", "Thunderbolt")
        self.addLegacyMove("Exeggutor", "Confusion")
        self.addLegacyMove("Exeggutor", "Zen Headbutt")
        self.addLegacyMove("Farfetchd", "Cut")
        self.addLegacyMove("Fearow", "Twister")
        self.addLegacyMove("Feraligator", "Water Gun")
        self.addLegacyMove("Flareon", "Heat Wave")
        self.addLegacyMove("Gastly", "Sucker Punch")
        self.addLegacyMove("Gastly", "Ominous Wind")
        self.addLegacyMove("Gengar", "Shadow Claw")
        self.addLegacyMove("Gengar", "Lick")
        self.addLegacyMove("Gengar", "Sludge Wave")
        self.addLegacyMove("Gengar", "Dark Pulse")
        self.addLegacyMove("Gengar", "Psychic")
        self.addLegacyMove("Golbat", "Ominous Wind")
        self.addLegacyMove("Golem", "Mud Shot")
        self.addLegacyMove("Golem", "Ancient Power")
        self.addLegacyMove("Golem", "Rock Slide")
        self.addLegacyMove("Graveler", "Mud Shot")
        self.addLegacyMove("Grimer", "Acid")
        self.addLegacyMove("Gyarados", "Dragon Breath")
        self.addLegacyMove("Gyarados", "Dragon Tail")
        self.addLegacyMove("Gyarados", "Dragon Pulse")
        self.addLegacyMove("Gyarados", "Twister")
        self.addLegacyMove("Haunter", "Lick")
        self.addLegacyMove("Haunter", "Shadow Ball")
        self.addLegacyMove("Hitmonchan", "Rock Smash")
        self.addLegacyMove("Hitmonchan", "Brick Break")
        self.addLegacyMove("Hitmonlee", "Stomp")
        self.addLegacyMove("Hitmonlee", "Brick Break")
        self.addLegacyMove("Hypno", "Psyshock")
        self.addLegacyMove("Hypno", "Shadow Ball")
        self.addLegacyMove("Igglybuff", "Body Slam")
        self.addLegacyMove("Jigglypuff", "Play Rough")
        self.addLegacyMove("Jigglypuff", "Body Slam")
        self.addLegacyMove("Jynx", "Pound")
        self.addLegacyMove("Jynx", "Ice Punch")
        self.addLegacyMove("Kabutops", "Fury Cutter")
        self.addLegacyMove("Kangaskhan", "Brick Break")
        self.addLegacyMove("Kangaskahn", "Stomp")
        self.addLegacyMove("Kingdra", "Water Gun")
        self.addLegacyMove("Kingler", "Mud Shot")
        self.addLegacyMove("Koffing", "Acid")
        self.addLegacyMove("Kyogre", "Dragon Tail")
        self.addLegacyMove("Lapras", "Ice Shard")
        self.addLegacyMove("Lapras", "Dragon Pulse")
        self.addLegacyMove("Lapras", "Ice Beam")
        self.addLegacyMove("Loudred", "Crunch")
        self.addLegacyMove("Machamp", "Karate Chop")
        self.addLegacyMove("Machamp", "Cross Chop")
        self.addLegacyMove("Machamp", "Stone Edge")
        self.addLegacyMove("Machamp", "Submission")
        self.addLegacyMove("Machoke", "Cross Chop")
        self.addLegacyMove("Machop", "Low Kick")
        self.addLegacyMove("Magby", "Flamethrower")
        self.addLegacyMove("Magneton", "Thunder Shock")
        self.addLegacyMove("Magneton", "Discharge")
        self.addLegacyMove("Meowth", "Body Slam")
        self.addLegacyMove("Mew", "Hurricane")
        self.addLegacyMove("Mew", "Dragon Pulse")
        self.addLegacyMove("Milotic", "Water Gun")
        self.addLegacyMove("Moltres", "Ember")
        self.addLegacyMove("Moltres", "Flamethrower")
        self.addLegacyMove("Muk", "Acid")
        self.addLegacyMove("Muk", "Lick")
        self.addLegacyMove("Nidoking", "Fury Cutter")
        self.addLegacyMove("Ninetales", "Ember")
        self.addLegacyMove("Ninetales", "Fire Blast")
        self.addLegacyMove("Ninetales", "Flamethrower")
        self.addLegacyMove("Omanyte", "Rock Tomb")
        self.addLegacyMove("Omanyte", "Brine")
        self.addLegacyMove("Omastar", "Rock Throw")
        self.addLegacyMove("Omastar", "Rock Slide")
        self.addLegacyMove("Onix", "Iron Head")
        self.addLegacyMove("Onix", "Rock Slide")
        self.addLegacyMove("Parasect", "Bug Bite")
        self.addLegacyMove("Persian", "Night Slash")
        self.addLegacyMove("Pichu", "Quick Attack")
        self.addLegacyMove("Pidgeot", "Wing Attack")
        self.addLegacyMove("Pidgeot", "Air Cutter")
        self.addLegacyMove("Pikachu", "Present") # December 2017
        self.addLegacyMove("Pikachu", "Thunder")
        self.addLegacyMove("Pinsir", "Fury Cutter")
        self.addLegacyMove("Pinsir", "Submission")
        self.addLegacyMove("Politoed", "Earthquake")
        self.addLegacyMove("Poliwhirl", "Scald")
        self.addLegacyMove("Poliwrath", "Mud Shot")
        self.addLegacyMove("Poliwrath", "Submission")
        self.addLegacyMove("Ponyta", "Fire Blash")
        self.addLegacyMove("Porygon", "Quick Attack")
        self.addLegacyMove("Porygon", "Tackle")
        self.addLegacyMove("Porygon", "Zen Headbutt")
        self.addLegacyMove("Porygon", "Discharge")
        self.addLegacyMove("Porygon", "Psybeam")
        self.addLegacyMove("Porygon", "Signal Beam")
        self.addLegacyMove("Primeape", "Karate Chop")
        self.addLegacyMove("Primeape", "Cross Chop")
        self.addLegacyMove("Raichu", "Thunder Shock")
        self.addLegacyMove("Raichu", "Thunder")
        self.addLegacyMove("Rapidash", "Ember")
        self.addLegacyMove("Rhydon", "Megahorn")
        self.addLegacyMove("Sandshrew", "Rock Tomb")
        self.addLegacyMove("Scyther", "Steel Wing")
        self.addLegacyMove("Scyther", "Bug Buzz")
        self.addLegacyMove("Seadra", "Blizzard")
        self.addLegacyMove("Seaking", "Poison Jab")
        self.addLegacyMove("Seaking", "Icy Wind")
        self.addLegacyMove("Seaking", "Drill Run")
        self.addLegacyMove("Seel", "Water Gun")
        self.addLegacyMove("Seel", "Aqua Jet")
        self.addLegacyMove("Smoochum", "Frost Breath")
        self.addLegacyMove("Snorlax", "Body Slam")
        self.addLegacyMove("Spearow", "Twister")
        self.addLegacyMove("Starmie", "Quick Attack")
        self.addLegacyMove("Starmie", "Tackle")
        self.addLegacyMove("Starmie", "Psybeam")
        self.addLegacyMove("Staryu", "Quick Attack")
        self.addLegacyMove("Suicune", "Hidden Power")
        self.addLegacyMove("Tangela", "Power Whip")
        self.addLegacyMove("Togepi", "Zen Headbutt")
        self.addLegacyMove("Togetic", "Steel Wing")
        self.addLegacyMove("Togetic", "Zen Headbutt")
        self.addLegacyMove("Venomoth", "Bug Bite")
        self.addLegacyMove("Venomoth", "Poison Fang")
        self.addLegacyMove("Venusaur", "Frenzy Plant")
        self.addLegacyMove("Voltorb", "Signal Beam")
        self.addLegacyMove("Weepinbell", "Razor Leaf")
        self.addLegacyMove("Weezing", "Acid")
        self.addLegacyMove("Zapdos", "Thunder Shock")
        self.addLegacyMove("Zapdos", "Discharge")
        self.addLegacyMove("Zubat", "Sludge Bomb")

        self.addLegacyMove("Meganium", "Frenzy Plant")



        self.addLegacyMove("Mareep", "Dragon Pulse") # Community day 4/2018
        self.addLegacyMove("Pikachu", "Surf") # Community day 1/2018
        self.addLegacyMove("Dragonite", "Draco Meteor") # Community Day March 2018


        self.addLegacyMove("Articuno", "Hurricane")
        self.addLegacyMove("Moltres", "Sky Attack")
        self.addLegacyMove("Zapdos", "Sky Attack")
        self.addLegacyMove("Blastoise", "Hydro Cannon")
        self.addLegacyMove("Tyranitar", "Smack Down")
        self.addLegacyMove("Charizard", "Blast Burn")

        self.addLegacyMove("Metagross", "Meteor Mash")
        self.addLegacyMove("Typhlosion", "Blast Burn")
        self.addLegacyMove("Feraligatr", "Hydro Cannon")
        self.addLegacyMove("Mamoswine", "Ancient Power")
        self.addLegacyMove("Sceptile", "Frenzy Plant")
        self.addLegacyMove("Salamence", "Outrage")
        self.addLegacyMove("Blaziken", "Blast Burn")
        self.addLegacyMove("Blaziken", "Blaze Kick")


        self.addLegacyMove("Ampharos", "Dragon Pulse")

        self.addLegacyMove("Mewtwo", "Shadow Ball")
        self.addLegacyMove("Mewtwo", "Hyper Beam")

        self.addLegacyMove("Eevee", "Last Resort")
        self.addLegacyMove("Flareon", "Last Resort")
        self.addLegacyMove("Jolteon", "Last Resort")
        self.addLegacyMove("Vaporeon", "Last Resort")
        self.addLegacyMove("Espeon", "Last Resort")
        self.addLegacyMove("Umbreon", "Last Resort")
