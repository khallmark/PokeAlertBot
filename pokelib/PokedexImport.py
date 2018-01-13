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

    def importWeather(self, weatherData):

        dbMap = self.createMap(Weather)
        weatherMap = {}

        for weather in weatherData:
            templateId = weather["templateId"]
            name = weather["weatherAffinities"]["weatherCondition"].capitalize()

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

                dbMap[templateId] = weatherObj

            weatherObj.save()

        return dbMap

    def importPokemon(self, pokemonData, types, weather):
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

            if len(pokemonObj.description) == 0 || pokemonObj.descrption is None:
                pokemonObj.description = self.getDescription(name.lower())
                
            pokemonObj.save()

    def getDescription(self, pokemon):
        page = requests.get("https://www.pokemon.com/us/pokedex/" + pokemon)

        content = page.text.replace('\n', ' ')

        tree = html.fromstring(content)

        description = tree.xpath('//p[@class="version-y                                   active"]/text()')

        if (len(description)):
            return description[0].strip()

        print(pokemon)
        exit(0)