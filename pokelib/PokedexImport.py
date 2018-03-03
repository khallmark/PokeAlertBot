from pokelib.documents import *
from lxml import html
import requests
import pokebase

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

            attackScalars = type["typeEffective"]["attackScalar"]

            for index, scalar in enumerate(attackScalars):
                type_name = Type.type_order[index]

                typeObj.typeIndex[type_name] = scalar

                dbMap[type_name].setDefenseType(templateId, scalar)

            dbMap[templateId] = typeObj

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

            #templateId = move["templateId"]

            moveSettings = move["moveSettings"]

            templateId = moveSettings["movementId"]
            name = moveSettings["movementId"].replace("_FAST", "").replace("_", " ").title()

            if templateId in dbMap:
                moveObj = dbMap[templateId]
            else:
                moveObj = Move(
                    templateId = templateId,
                    name = name
                )

            moveObj.name = name

            charge = True
            if "_FAST" in templateId:
                charge = False

            moveObj.charge = charge

            if moveSettings["pokemonType"] in types:
                moveObj.type = types[moveSettings['pokemonType']]

            moveObj.durationMS = moveSettings["durationMs"]

            if "energyDelta" in moveSettings:
                moveObj.energyDelta = moveSettings["energyDelta"]
            else:
                print(name)


            if "staminaLossScalar" in moveSettings:
                moveObj.staminaLossScalar = moveSettings["staminaLossScalar"]
            else:
                print(name)

            moveObj.damageWindowStart = moveSettings["damageWindowStartMs"]
            moveObj.damageWindowEnd   = moveSettings["damageWindowEndMs"]


            if "power" in moveSettings:
                moveObj.power = moveSettings["power"]
            else:
                moveObj.power = 0

            moveObj.save()

            dbMap[templateId] = moveObj

        return dbMap

    def importPokemon(self, pokemonData, types, weather, moves):
        dbMap = self.createMap(Pokemon)

        pokemon_dict = []
        for pokemon in pokemonData:
            pokemonObj = False

            templateId = pokemon["templateId"]

            pokemonNumber = int(templateId.split("_")[0][1:])

            pokemonSettings = pokemon["pokemonSettings"]
            name = pokemonSettings["pokemonId"].title().replace("_", "-")

            if templateId in dbMap:
                pokemonObj = dbMap[templateId]
            else:
                pokemonObj = Pokemon(
                    templateId = templateId,
                    name = name
                )

            pokemonObj.source = "game_master"
            pokemonObj.name = name
            pokemonObj.number = pokemonNumber
            pokemonObj.generation = self.generation(pokemonNumber)
            pokemonObj.type = types[pokemonSettings["type"]]

            self.loadPokeAPIData(pokemonObj)

            if "type2" in pokemonSettings:
                pokemonObj.type2 = types[pokemonSettings["type2"]]

            pokemonObj.baseAttack  = pokemonSettings['stats']['baseAttack']
            pokemonObj.baseDefense = pokemonSettings['stats']['baseDefense']
            pokemonObj.baseStamina = pokemonSettings['stats']['baseStamina']

            if pokemonObj.description is None or pokemonObj.category is None:
                self.loadPokedexData(name.lower(), pokemonObj)

            stabMoves = []

            quickMoves = []
            for quickMove in pokemonSettings["quickMoves"]:
                if quickMove in moves:
                    move = moves[quickMove]

                    quickMoves.append(move)
                    if move.type == pokemonObj.type or (pokemonObj.type2 is not None and move.type == pokemonObj.type2):
                        stabMoves.append(move)

            chargeMoves = []
            for chargeMove in pokemonSettings["cinematicMoves"]:
                if chargeMove in moves:
                    move = moves[chargeMove]

                    chargeMoves.append(moves[chargeMove])

                    if move.type == pokemonObj.type or (pokemonObj.type2 is not None and move.type == pokemonObj.type2):
                        stabMoves.append(move)


            pokemonObj.quickMoves = quickMoves
            pokemonObj.chargeMoves = chargeMoves
            pokemonObj.stabMoves = stabMoves

            pokemonObj.save()

        return pokemonObj

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

        return generation

    def loadPokedexData(self, pokemon, pokemonObj):
        page = requests.get("https://www.pokemon.com/us/pokedex/" + pokemon)

        if page.status_code == 503 or page.status_code == 404:
            print(pokemon)
            exit(0)

        content = page.text.replace('\n', ' ')

        tree = html.fromstring(content)

        description = tree.xpath('//p[@class="version-y                                   active"]/text()')

        if (len(description)):
            pokemonObj.description = description[0].strip()

        category = tree.xpath('//div[@class="column-7 push-7"]/ul/li/span[@class="attribute-value"]/text()')

        pokemonObj.category = category[0].strip()

    def loadPokeAPIData(self, pokemonObj):
        apiMon = pokebase.NamedAPIResource("pokemon", pokemonObj.number)

        pokemonObj.weight = apiMon.weight/10
        pokemonObj.height = apiMon.height/10

        apiSpecies = pokebase.NamedAPIResource("pokemon-species", pokemonObj.number)

