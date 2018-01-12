import bot.lbhbot as bot
from pokelib import Pokedex

client = bot.LBHBot(
    token='Mzk0NTkxMzkyMTgzMjIyMjc1.DSGjbA.Ta1Pwzksn_a8UmlGvWAJ7DeDs3I',
    cleverToken="CC60wa5HXQXrI31bpwFpfeEw_qA",
    pokedex=Pokedex.Pokedex()
)

client.addFileChannel("349042487924490242")
client.addFileChannel("396193424220618763")