import os
from mongoengine import *
import bot.lbhbot as bot
from pokelib.Pokedex import Pokedex

connect('pokemon', host='localhost', port=27017)

token = "Mzk0NTkxMzkyMTgzMjIyMjc1.DSGjbA.Ta1Pwzksn_a8UmlGvWAJ7DeDs3I"

if os.getenv("BIRCH_BETA", 0):
    token = "NDE3MTYzMDkzMjIzOTMxOTA0.DXPA7w.GhuGDyvLcM9E2JpQ2oMto--RfOU"

client = bot.LBHBot(
    token=token,
    cleverToken="CC60wa5HXQXrI31bpwFpfeEw_qA",
    pokedex=Pokedex()
)

#
# client.addFileChannel("349042487924490242")
# client.addFileChannel("396193424220618763")

# Features: Message logging by user, command, server
# Catch Rate
# Add external emoji to perm issions +