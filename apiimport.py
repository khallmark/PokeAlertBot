import json

from pokelib.PokeApiImport import PokeApiImport
from pokelib.documents import *
from mongoengine import *
from pprint import pprint
import pokebase
import pokebase.api as api

api.set_cache("./pokebase_cache")

connect('pokemon', host='localhost', port=27017)


importer = PokeApiImport()

# pokemon = importer.importPokemon(475)
# pokemon.save()

i = 387
while i < 802:
    pokemon = importer.importPokemon(i)

    if pokemon is not None:
        pokemon.save()

    i += 1


#
# pokemon_data = json.load(open('output/pokemons.json'))
# spawn_data   = json.load(open('output/spawns.json'))
# type_data    = json.load(open('output/types.json'))
# weather_data = json.load(open('output/missed.json'))
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