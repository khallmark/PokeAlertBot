import json
from pprint import pprint

from pokelib.documents import *

from mongoengine import *

connect('pokemon', host='localhost', port=27017)

class Pokedex:
    def __init__(self):
        self.test = 0

    def getPokemon(self, pokemon):
        results = Pokemon.objects(name=pokemon)

        if len(results) > 0:
            return results[0]

        return None