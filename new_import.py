import json
import os
from collections import OrderedDict

from pprint import pprint


from pokelib.PokedexImport import PokedexImport
from pokelib.BirchImporter import BirchImporter
from pokelib.documents import *
from mongoengine import *
import pokebase
import pokebase.api as api


'''
Pokemon Import Steps

1. Import Game_Master 
2. Import PokeAPI starting from 1. Check for "varieties" in pokemon-species. If "game_master" import, only import some 
'''

importer = BirchImporter()

importer.dex_import('game_master/versions/latest/GAME_MASTER.json')

