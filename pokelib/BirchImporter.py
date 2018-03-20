import json
import os
# from collections import OrderedDict
from pprint import pprint

class BirchImporter:

    def dex_import(self, json_file):
        data = self.parse_game_master(json_file, ['pokemons', 'spawns', 'types', 'weather', 'moves'])

        pprint(data)

        # api.set_cache("./pokebase_cache")
        #
        # connect('pokemon', host='localhost', port=27017)
        #
        # pokemon_data = json.load(open('output/pokemons.json'))
        # spawn_data   = json.load(open('output/spawns.json'))
        # type_data    = json.load(open('output/types.json'))
        # weather_data = json.load(open('output/weather.json'))
        # move_data = json.load(open('output/moves.json'))
        #
        #
        # importer = PokedexImport()
        #
        # types = importer.importTypes(type_data)
        # weather = importer.importWeather(weather_data, types)
        # moves = importer.importMoves(move_data, types)
        #
        # importer.importPokemon(pokemon_data, types, weather, moves)

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