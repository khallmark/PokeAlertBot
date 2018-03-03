import requests
import pokebase
from pprint import pprint
from lxml import html

from pokelib.documents import *

class PokeApiImport:

    def importPokemon(self, pokemon):

        apiMon = pokebase.NamedAPIResource("pokemon", pokemon)

        results = Pokemon.objects(name__iexact=apiMon.name.title())

        if len(results) > 0:
            pokemonObj = results[0]
        else:
            pokemonObj = Pokemon()
            pokemonObj.name = apiMon.name.title()

        # print(pokemonObj.name)

        stats = {}
        for stat in apiMon.stats:
            statName = stat.stat.name
            statValue = stat.base_stat

            stats[statName] = statValue

        pokemonObj.source = "pokeapi"
        pokemonObj.number = apiMon.id
        pokemonObj.generation = self.generation(apiMon.id)
        pokemonObj.templateId = "V" + str(pokemonObj.number).zfill(4) + "_POKEMON_" + pokemonObj.name.upper()

        pokemonObj.baseAttack = self.calculatePogoAttack(stats["attack"], stats["special-attack"], stats["speed"])
        pokemonObj.baseDefense = self.calculatePogoDefense(stats["defense"], stats["special-defense"], stats["speed"])
        pokemonObj.baseStamina = self.calculatePogoStamina(stats["hp"])

        pokemonObj.weight = apiMon.weight/10
        pokemonObj.height = apiMon.height/10


        for type in apiMon.types:
            name = type.type.name

            typeObj = Type.objects(name__iexact=name)[0]

            if type.slot == 1:
                pokemonObj.type = typeObj
            elif type.slot == 2:
                pokemonObj.type2 = typeObj

        for move in apiMon.moves:
            self.importPokemonMove(pokemonObj, move)

        if pokemonObj.description is None or pokemonObj.category is None:
            if not self.loadPokedexData(pokemonObj.name.lower(), pokemonObj):
                return None

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

    def importPokemonMove(self, pokemonObj, move):
        version_group_details = move.version_group_details

        moveName = move.move.name.replace('-', ' ').title()

        moves = Move.objects(name__iexact=moveName)

        if len(moves) == 0:
            return

        learnMethod = False
        for learnMethod in version_group_details:
            if learnMethod["move_learn_method"]['name'] == "level-up":
                learnMethod = True
                break

        if not learnMethod:
            return

        moveObj = moves[0]

        if moveObj.type == pokemonObj.type or (pokemonObj.type2 is not None and moveObj.type == pokemonObj.type2):
            pokemonObj.stabMoves.append(moveObj)

        if moveObj.charge and moveObj not in pokemonObj.chargeMoves:
            pokemonObj.chargeMoves.append(moveObj)
        elif moveObj not in pokemonObj.quickMoves:
            pokemonObj.quickMoves.append(moveObj)

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

        higher = (7/8)*higher
        lower = (1/8)*lower

        scaledAttack = round(2*(higher+lower))
        speedMod =  1+(speed - 75)/500

        baseDefense = round(scaledAttack*speedMod)

        return baseDefense

    def calculatePogoStamina(self, hp):
        return 2*hp