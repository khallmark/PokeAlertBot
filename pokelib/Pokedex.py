from pokelib.documents import *

class Pokedex:
    def __init__(self):
        self.test = 0

    def getPokemon(self, pokemon):

        if pokemon.isdigit():
            results = Pokemon.objects(number=pokemon)
        else:
            results = Pokemon.objects(name__iexact=pokemon)

        if len(results) > 0:
            return results[0]

        return None

    def getType(self, type):
        results = Type.objects(name__iexact=type)

        if len(results) > 0:
            return results[0]

        return None

    def getMove(self, move):
        results = Move.objects(name__iexact=move)

        if len(results) > 0:
            return results[0]

        return None