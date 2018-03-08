import json

from pokelib.PokedexImport import PokedexImport
from pokelib.documents import *
from mongoengine import *
import pokebase
import pokebase.api as api

api.set_cache("./pokebase_cache")

connect('pokemon', host='localhost', port=27017)

pokemon_data = json.load(open('output/pokemons.json'))
spawn_data   = json.load(open('output/spawns.json'))
type_data    = json.load(open('output/types.json'))
weather_data = json.load(open('output/weather.json'))
move_data = json.load(open('output/moves.json'))


importer = PokedexImport()

types = importer.importTypes(type_data)
weather = importer.importWeather(weather_data, types)
moves = importer.importMoves(move_data, types)

pokemons = importer.importPokemon(pokemon_data, spawn_data, types, weather, moves)

importer.addLegacyMoves()

'''
Pokemon Import Steps

1. Import Game_Master 
2. Import PokeAPI starting from 1. Check for "varieties" in pokemon-species. If "game_master" import, only import some 
'''