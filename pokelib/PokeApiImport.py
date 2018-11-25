import requests
import pokebase
from pprint import pprint
from lxml import html

from pokelib.documents import *

class PokeApiImport:
    def importAPIPokemon(self, pokemon, pokemonVariety = 0):

        hasVariety = True
        if pokemonVariety == 0:
            hasVariety = False
            pokemonVariety = pokemon

        apiSpecies = pokebase.NamedAPIResource("pokemon-species", pokemon)
        apiMon = pokebase.NamedAPIResource("pokemon", pokemonVariety)

        species = apiSpecies.name.title()

        if hasVariety:
            name = apiMon.name.title()
        else:
            name = species

        results = Pokemon.objects(name__iexact=name)

        if len(results) > 0:
            pokemonObj = results[0]
        else:
            pokemonObj = Pokemon()
            pokemonObj.name = name
            pokemonObj.source = "pokeapi"

        pokemonObj.species = species
        pokemonObj.number = pokemon

        if hasVariety == False:
            self.importVarieties(pokemonObj, apiSpecies)

        # print(pokemonObj.name)

        stats = {}
        for stat in apiMon.stats:
            statName = stat.stat.name
            statValue = stat.base_stat

            stats[statName] = statValue

        # if pokemonObj.source != "pokeapi":
        #     return

        pokemonObj.number = apiSpecies.id
        pokemonObj.generation = self.generation(apiSpecies.id)
        pokemonObj.templateId = "V" + str(pokemonObj.number).zfill(4) + "_POKEMON_" + pokemonObj.name.upper()

        pokemonObj.baseAttack = self.calculatePogoAttack(stats["attack"], stats["special-attack"], stats["speed"])
        pokemonObj.baseDefense = self.calculatePogoDefense(stats["defense"], stats["special-defense"], stats["speed"])
        pokemonObj.baseStamina = self.calculatePogoStamina(stats["hp"])

        pokemonObj.weight = apiMon.weight/10
        pokemonObj.height = apiMon.height/10


        gender_rate = apiSpecies.gender_rate

        if gender_rate == -1:
            pokemonObj.gender = None
        else:
            gender = PokemonGender()

            gender.male = (8-gender_rate)/8
            gender.female = gender_rate/8

            pokemonObj.gender = gender

        for type in apiMon.types:
            name = type.type.name

            typeObj = Type.objects(name__iexact=name)[0]

            if type.slot == 1:
                pokemonObj.type = typeObj
            elif type.slot == 2:
                pokemonObj.type2 = typeObj


        self.importPokemonMove(pokemonObj, apiMon.moves)

        return pokemonObj

    def importVarieties(self, pokemonObj, apiSpecies):
        if apiSpecies.varieties is not None:
            varieties = []
            for variety in apiSpecies.varieties:
                varietyName = variety.pokemon.name.title()
                if pokemonObj.name != varietyName:
                    print(apiSpecies.name + "/" + varietyName)
                    varieties.append(varietyName)
                    varietyUrl = variety.pokemon.url
                    varietyNum = varietyUrl.rsplit('/', 1)[-1]

                    varietyMon = self.importAPIPokemon(pokemonObj.number, varietyNum)

                    if (varietyMon is not None):
                        varietyMon.save()

            pokemonObj.varieties = varieties

    def importGMPokemon(self, pokemonObj):
        # apiMon = pokebase.NamedAPIResource("pokemon", pokemonObj.number)
        #
        # pokemonObj.weight = apiMon.weight/10
        # pokemonObj.height = apiMon.height/10

        apiSpecies = pokebase.NamedAPIResource("pokemon-species", pokemonObj.number)

        pokemonName = pokemonObj.name.lower().replace('female', 'f').replace("male", "m")

        if pokemonName == "deoxys":
            pokemonName = "deoxys-normal"

        try:
            apiMon = pokebase.NamedAPIResource("pokemon", pokemonName)
        except:
            apiMon = pokebase.NamedAPIResource("pokemon", pokemonObj.number)

        # @todo Remove this when the game master updates
        # stats = {}
        # for stat in apiMon.stats:
        #     statName = stat.stat.name
        #     statValue = stat.base_stat
        #
        #     stats[statName] = statValue
        #
        # pokemonObj.baseAttack = self.calculatePogoAttack(stats["attack"], stats["special-attack"], stats["speed"])
        # pokemonObj.baseDefense = self.calculatePogoDefense(stats["defense"], stats["special-defense"], stats["speed"])
        # pokemonObj.baseStamina = self.calculatePogoStamina(stats["hp"])

        self.importVarieties(pokemonObj, apiSpecies)

        gender_rate = apiSpecies.gender_rate

        if gender_rate == -1:
            pokemonObj.gender = None
        else:
            gender = PokemonGender()

            gender.male = (8-gender_rate)/8
            gender.female = gender_rate/8

            pokemonObj.gender = gender

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

    def importPokemonMove(self, pokemonObj, moves):
        quickMoves = []
        chargeMoves = []
        stabMoves = []

        for move in moves:
            version_group_details = move.version_group_details

            moveName = move._APIMetadata__data["move"]["name"].replace('-', ' ').title()

            movesResult = Move.objects(name__iexact=moveName)

            if len(movesResult) == 0:
                continue

            learnMethod = False
            for learnMethod in version_group_details:
                if learnMethod["move_learn_method"]['name'] == "level-up":
                    learnMethod = True
                    break

            if not learnMethod:
                continue

            moveObj = movesResult[0]

            if moveObj.type == pokemonObj.type or (pokemonObj.type2 is not None and moveObj.type == pokemonObj.type2):
                stabMoves.append(moveObj)

            if moveObj.charge:
                chargeMoves.append(moveObj)
            else:
                quickMoves.append(moveObj)

        pokemonObj.quickMoves = quickMoves
        pokemonObj.chargeMoves = chargeMoves
        pokemonObj.stabMoves = stabMoves

    # Loads accurate flavor text and genera from the Pokémon Website
    def loadPokedexData(self, pokemon, pokemonObj):
        page = requests.get("https://www.pokemon.com/us/pokedex/" + pokemon)

        if page.status_code == 503 or page.status_code == 404:
            print(pokemon)
            return False

        content = page.text.replace('\n', ' ')

        tree = html.fromstring(content)

        description = tree.xpath('//p[@class="version-y                                   active"]/text()')

        if (len(description)):
            pokemonObj.description = description[0].strip()

        category = tree.xpath('//div[@class="column-7 push-7"]/ul/li/span[@class="attribute-value"]/text()')

        pokemonObj.category = category[0].strip()

        return True

    def calculatePogoAttack(self, attack, specialAttack, speed):
        higher = attack
        lower = specialAttack

        if lower > higher:
            higher = specialAttack
            lower = attack

        higher = (7/8)*higher
        lower = (1/8)*lower

        scaledAttack = round(2*(higher+lower))
        speedMod =  1+(speed - 75)/500

        baseAttack = round(scaledAttack*speedMod)

        return baseAttack

    def calculatePogoDefense(self, defense, specialDefense, speed):
        higher = defense
        lower = specialDefense

        if lower > higher:
            higher = specialDefense
            lower = defense

        higher = (5/8)*higher
        lower = (3/8)*lower

        scaledAttack = round(2*(higher+lower))
        speedMod =  1+(speed - 75)/500

        baseDefense = round(scaledAttack*speedMod)

        return baseDefense

    def calculatePogoStamina(self, hp):
        return math.floor(1.75 * hp + 50)