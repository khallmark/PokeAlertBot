from pokelib.documents import *
from lxml import html
import requests

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
                typeObj = Type(
                    templateId = templateId,
                    name = name
                )

                dbMap[templateId] = typeObj

            typeObj.setTypeMap(type["typeEffective"]["attackScalar"])

            typeObj.save()

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

            pokemonObj.name = name
            pokemonObj.number = pokemonNumber
            pokemonObj.type = types[pokemonSettings["type"]]

            if "type2" in pokemonSettings:
                pokemonObj.type2 = types[pokemonSettings["type2"]]

            pokemonObj.baseAttack  = pokemonSettings['stats']['baseAttack']
            pokemonObj.baseDefense = pokemonSettings['stats']['baseDefense']
            pokemonObj.baseStamina = pokemonSettings['stats']['baseStamina']

            if pokemonObj.description is None or pokemonObj.category is None:
                self.loadPokedexData(name.lower(), pokemonObj)

            quickMoves = []
            for quickMove in pokemonSettings["quickMoves"]:
                if quickMove in moves:
                    quickMoves.append(moves[quickMove])

            pokemonObj.quickMoves = quickMoves

            chargeMoves = []
            for chargeMove in pokemonSettings["cinematicMoves"]:
                if chargeMove in moves:
                    chargeMoves.append(moves[chargeMove])

            pokemonObj.chargeMoves = chargeMoves

            pokemonObj.save()

    def loadPokedexData(self, pokemon, pokemonObj):
        page = requests.get("https://www.pokemon.com/us/pokedex/" + pokemon)

        if page.status_code == 503:
            print(pokemon)
            exit(0)

        content = page.text.replace('\n', ' ')

        tree = html.fromstring(content)

        description = tree.xpath('//p[@class="version-y                                   active"]/text()')

        if (len(description)):
            pokemonObj.description = description[0].strip()

        category = tree.xpath('//div[@class="column-7 push-7"]/ul/li/span[@class="attribute-value"]/text()')

        pokemonObj.category = category[0].strip()