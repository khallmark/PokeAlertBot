from pokelib.documents import *

class Pokedex:
    def __init__(self):
        self.test = 0

    def getPokemon(self, pokemon):
        results = Pokemon.objects(name=pokemon)

        if len(results) > 0:
            return results[0]

        return None