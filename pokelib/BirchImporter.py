import json
import os
import requests

from lxml import html
from time import sleep


# from collections import OrderedDict
from pprint import pprint

from mongoengine import *
import pokebase.api as api

from pokelib.PokedexImport import PokedexImport
from pokelib.PokeApiImport import PokeApiImport


class BirchImporter:
    def __init__(self):
        api.set_cache("./pokebase_cache")

        connect('pokemon_import_test', host='localhost', port=27017)

    '''
    Pokemon Import Steps

    1. Import Game_Master
    2. Import PokeAPI starting from 1. Check for "varieties" in pokemon-species. If "game_master" import, only import some
    '''
    def dex_import(self, json_file):
        data = self.parse_game_master(json_file, ['pokemons', 'spawns', 'types', 'weather', 'moves'])

        dexImporter = PokedexImport()

        types = dexImporter.importTypes(data['types'])
        weather = dexImporter.importWeather(data['weather'], types)
        moves = dexImporter.importMoves(data['moves'], types)

        pokemons = dexImporter.importPokemon(data['pokemons'], data['spawns'], types, weather, moves)

        dexImporter.addLegacyMoves()

        apiImporter = PokeApiImport()

        i = 387
        while i < 802:

            ## load pokemon object
            ## if game_master:
            ##      import data for gm record
            ## else
            ##      import whole record from pokeapi.co

            pokemon = apiImporter.importPokemon(i)

            self.loadPokedexData(pokemon)

            if pokemon is not None:
                pokemon.save()

            i += 1

    def loadPokedexData(self, pokemonObj):
        pokemon = pokemonObj.name

        cache_file = "./pokemon_cache/" + pokemon + ".html"

        content = None
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as htmlFile:
                content = htmlFile.read()
        else:
            page = requests.get("https://www.pokemon.com/us/pokedex/" + pokemon)

            while page.status_code == 503 or page.status_code == 404:
                sleep(1)
                page = requests.get("https://www.pokemon.com/us/pokedex/" + pokemon)

            content = page.text.replace('\n', ' ')

            open(cache_file, 'w').write(content)


        tree = html.fromstring(content)

        description = tree.xpath('//p[@class="version-y                                   active"]/text()')

        if (len(description)):
            pokemonObj.description = description[0].strip()

        category = tree.xpath('//div[@class="column-7 push-7"]/ul/li/span[@class="attribute-value"]/text()')

        pokemonObj.category = category[0].strip()

    def parse_game_master(self, json_file, categories = []):

        masterNew = json.load(open(json_file))

        masterNewIn = masterNew['itemTemplates']

        general = {}

        docs = 'avatars', 'badges', 'settings', 'forms', 'items', 'types', 'quests', 'spawns', 'pokemons', 'moves', 'cameras', 'iaps', 'sequences', 'missed', 'weather'

        for doc in docs:
            general[doc] = []
        
        for a in masterNewIn:
            if a['templateId'].startswith('AVATAR_'):
                general['avatars'].append(a)
            elif a['templateId'].startswith('BADGE_'):
                general['badges'].append(a)
            elif a['templateId'].endswith('_SETTINGS'):
                general['settings'].append(a)
            elif a['templateId'].startswith('FORMS_'):
                general['forms'].append(a)
            elif a['templateId'].startswith('ITEM_'):
                general['items'].append(a)
            elif a['templateId'].startswith('POKEMON_TYPE_'):
                general['types'].append(a)
            elif a['templateId'].startswith('QUEST_'):
                general['quests'].append(a)
            elif a['templateId'].startswith('SPAWN_'):
                general['spawns'].append(a)
            elif a['templateId'].startswith('_MOVE_', 5):
                general['moves'].append(a)
            elif a['templateId'].startswith('_POKEMON_', 5):
                general['pokemons'].append(a)
            elif a['templateId'].startswith('camera_'):
                general['cameras'].append(a)
            elif 'iapItemDisplay' in a and a['iapItemDisplay']['category'].startswith('IAP_'):
                general['iaps'].append(a)
            elif a['templateId'].startswith('sequence_'):
                general['sequences'].append(a)
            elif a['templateId'].startswith('WEATHER_'):
                general['weather'].append(a)
            else:
                general['missed'].append(a)

        if len(categories) > 0:
            output = {}

            for category in categories:
                if general[category] is not None:
                    output[category] = general[category]

            general = output

        return general