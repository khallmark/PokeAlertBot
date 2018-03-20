import json

from pokelib.PokedexImport import PokedexImport
from mongoengine import *
import pokebase.api as api
from pokelib.PokeApiImport import PokeApiImport

api.set_cache("./pokebase_cache")

connect('pokemon', host='localhost', port=27017)

# @todo Adjust this so it always pulls from the "latest" GAME_MASTER directly instead of relying on the parse script
pokemon_data = json.load(open('output/pokemons.json'))
spawn_data   = json.load(open('output/spawns.json'))
type_data    = json.load(open('output/types.json'))
weather_data = json.load(open('output/weather.json'))
move_data = json.load(open('output/moves.json'))

dexImporter = PokedexImport()

types = dexImporter.importTypes(type_data)
weather = dexImporter.importWeather(weather_data, types)
moves = dexImporter.importMoves(move_data, types)

pokemons = dexImporter.importPokemon(pokemon_data, spawn_data, types, weather, moves)

dexImporter.addLegacyMoves()

apiImporter = PokeApiImport()

i = 387
while i < 802:
    pokemon = apiImporter.importPokemon(i)

    if pokemon is not None:
        pokemon.save()

    i += 1

'''
Pokemon Import Steps

1. Import Game_Master 
2. Import PokeAPI starting from 1. Check for "varieties" in pokemon-species. If "game_master" import, only import some 
'''