from mongoengine import *
import bot.lbhbot as bot
from pokelib.Pokedex import Pokedex

connect('pokemon', host='localhost', port=27017)

client = bot.LBHBot(
    token='Mzk0NTkxMzkyMTgzMjIyMjc1.DSGjbA.Ta1Pwzksn_a8UmlGvWAJ7DeDs3I',
    cleverToken="CC60wa5HXQXrI31bpwFpfeEw_qA",
    pokedex=Pokedex()
)

client.addFileChannel("349042487924490242")
client.addFileChannel("396193424220618763")