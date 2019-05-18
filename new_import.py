from pokelib.BirchImporter import BirchImporter
from datetime import datetime

f = open("../last_updated", "w")

time = datetime.now()
f.write(time.strftime("%m/%d/%Y, %H:%M:%S"))
f.close()

importer = BirchImporter()

importer.dex_import('game_master/versions/latest/GAME_MASTER.json')

