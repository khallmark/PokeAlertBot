import math
from mongoengine import *

class Type(Document):
    type_order=[
        "POKEMON_TYPE_NORMAL",
        "POKEMON_TYPE_FIGHTING",
        "POKEMON_TYPE_FLYING",
        "POKEMON_TYPE_POISON",
        "POKEMON_TYPE_GROUND",
        "POKEMON_TYPE_ROCK",
        "POKEMON_TYPE_BUG",
        "POKEMON_TYPE_GHOST",
        "POKEMON_TYPE_STEEL",
        "POKEMON_TYPE_FIRE",
        "POKEMON_TYPE_WATER",
        "POKEMON_TYPE_GRASS",
        "POKEMON_TYPE_ELECTRIC",
        "POKEMON_TYPE_PSYCHIC",
        "POKEMON_TYPE_ICE",
        "POKEMON_TYPE_DRAGON",
        "POKEMON_TYPE_DARK",
        "POKEMON_TYPE_FAIRY"
    ]

    templateId = StringField(required=True)
    name = StringField(required=True, max_length=10)
    typeIndex = DictField()

    def setTypeMap(self, attackScalars):
        for index, scalar in enumerate(attackScalars):
            type_name = Type.type_order[index]
            self.typeIndex[type_name] = scalar


class Weather(Document):
    templateId = StringField(required=True)
    name = StringField(required=True)
    typeBoost = ListField(ReferenceField(Type))

class Move(Document):
    templateId = StringField(required=True)
    name = StringField()
    type = ReferenceField(Type)
    power = FloatField()
    durationMS = IntField()
    charge = BooleanField()

    def dps(self, pokemon, weather):
        power = self.power

        if power is None:
            power = 0

        if self in pokemon.stabMoves:
            power = power * 1.2

        if weather is not None and self.type in weather.typeBoost:
            power = power * 1.2

        duration = self.durationMS

        if self.charge:
            duration += 500

        return round((power * 1000)/duration, 1)

class Pokemon(Document):
    cpm_map = {
        "1":    0.094,
        "1.5":  0.135137432,
        "2":    0.16639787,
        "2.5":  0.192650919,
        "3":    0.21573247,
        "3.5":  0.236572661,
        "4":    0.25572005,
        "4.5":  0.273530381,
        "5":    0.29024988,
        "5.5":  0.306057377,
        "6":    0.3210876,
        "6.5":  0.335445036,
        "7":    0.34921268,
        "7.5":  0.362457751,
        "8":    0.37523559,
        "8.5":  0.387592406,
        "9":    0.39956728,
        "9.5":  0.411193551,
        "10":   0.42250001,
        "10.5": 0.432926419,
        "11":   0.44310755,
        "11.5": 0.4530599578,
        "12":   0.46279839,
        "12.5": 0.472336083,
        "13":   0.48168495,
        "13.5": 0.4908558,
        "14":   0.49985844,
        "14.5": 0.508701765,
        "15":   0.51739395,
        "15.5": 0.525942511,
        "16":   0.53435433,
        "16.5": 0.542635767,
        "17":   0.55079269,
        "17.5": 0.558830576,
        "18":   0.56675452,
        "18.5": 0.574569153,
        "19":   0.58227891,
        "19.5": 0.589887917,
        "20":   0.59740001,
        "20.5": 0.604818814,
        "21":   0.61215729,
        "21.5": 0.619399365,
        "22":   0.62656713,
        "22.5": 0.633644533,
        "23":   0.64065295,
        "23.5": 0.647576426,
        "24":   0.65443563,
        "24.5": 0.661214806,
        "25":   0.667934,
        "25.5": 0.674577537,
        "26":   0.68116492,
        "26.5": 0.687680648,
        "27":   0.69414365,
        "27.5": 0.700538673,
        "28":   0.70688421,
        "28.5": 0.713164996,
        "29":   0.71939909,
        "29.5": 0.725571552,
        "30":   0.7317,
        "30.5": 0.734741009,
        "31":   0.73776948,
        "31.5": 0.740785574,
        "32":   0.74378943,
        "32.5": 0.746781211,
        "33":   0.74976104,
        "33.5": 0.752729087,
        "34":   0.75568551,
        "34.5": 0.758630378,
        "35":   0.76156384,
        "35.5": 0.764486065,
        "36":   0.76739717,
        "36.5": 0.770297266,
        "37":   0.7731865,
        "37.5": 0.776064962,
        "38":   0.77893275,
        "38.5": 0.781790055,
        "39":   0.78463697,
        "39.5": 0.787473578,
        "40":   0.79030001
    }

    templateId = StringField(required=True)
    number = IntField()
    name = StringField(required=True)
    description = StringField()
    category = StringField()
    type = ReferenceField(Type)
    type2 = ReferenceField(Type)
    baseAttack = IntField()
    baseDefense = IntField()
    baseStamina = IntField()
    quickMoves = ListField(ReferenceField(Move))
    chargeMoves = ListField(ReferenceField(Move))
    stabMoves = ListField(ReferenceField(Move))
    evolutions = ListField(ReferenceField('self'))
    # familyId = StringField()

    def icon(self):
        number = str(self.number).zfill(3)

        return "https://serebii.net/pokemongo/pokemon/" + number + ".png";

    def cp(self, level, attackIV: int, defenseIV: int, staminaIV: int):
        # CP = (Attack * Defense^0.5 * Stamina^0.5 * CP_Multiplier^2) / 10
        if (attackIV > 15):
            attackIV = 15

        if (defenseIV > 15):
            defenseIV = 15

        if (staminaIV > 15):
            staminaIV = 15

        attack = self.baseAttack + attackIV
        defense = self.baseDefense + defenseIV
        stamina = self.baseStamina + staminaIV

        cp = math.floor(((attack) * math.pow(defense, 0.5) * math.pow(stamina, 0.5) * math.pow(Pokemon.cpm_map[str(level)], 2))/10)

        return cp