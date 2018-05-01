import os
from mongoengine import *
import bot.lbhbot as bot
from pokelib.Pokedex import Pokedex
import logging

logging.basicConfig(level=logging.INFO)
connect('pokemon', host='localhost', port=27017)

token = "Mzk0NTkxMzkyMTgzMjIyMjc1.DSGjbA.Ta1Pwzksn_a8UmlGvWAJ7DeDs3I"

if os.getenv("BIRCH_BETA", 0):
    token = "NDE3MTYzMDkzMjIzOTMxOTA0.DXPA7w.GhuGDyvLcM9E2JpQ2oMto--RfOU"

file_channels = [
    # May Fighting Event
    "441006333672685568",

    # magus66 Test Channel
    "349042487924490242",
]

client = bot.LBHBot(
    token=token,
    cleverToken="CC60wa5HXQXrI31bpwFpfeEw_qA",
    pokedex=Pokedex(),
    file_channels=file_channels
)