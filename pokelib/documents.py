import math
import datetime
from mongoengine import *

class Stat(Document):
    identifier = StringField()
    type = StringField() # channel, command, user
    count = IntField()

class MessageLog(Document):
    timestamp = DateTimeField(default=datetime.datetime.now)
    chanId = StringField()
    server = StringField()
    channel = StringField()
    user = StringField()
    length = IntField()

class CommandLog(Document):
    timestamp = DateTimeField(default=datetime.datetime.now)
    server = StringField()
    channel = StringField()
    user = StringField()
    command = StringField()
    message = StringField()


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
    
    type_colors = {
        "POKEMON_TYPE_NORMAL"   : 0x808179,
        "POKEMON_TYPE_FIGHTING" : 0xDA3E53,
        "POKEMON_TYPE_FLYING"   : 0x6780D6,
        "POKEMON_TYPE_POISON"   : 0xDD4FCD,
        "POKEMON_TYPE_GROUND"   : 0xC0703B,
        "POKEMON_TYPE_ROCK"     : 0xC8BA56,
        "POKEMON_TYPE_BUG"      : 0x91CD04,
        "POKEMON_TYPE_GHOST"    : 0x9778DC,
        "POKEMON_TYPE_STEEL"    : 0x248788,
        "POKEMON_TYPE_FIRE"     : 0xFC931A,
        "POKEMON_TYPE_WATER"    : 0x50B0D9,
        "POKEMON_TYPE_GRASS"    : 0x43C96C,
        "POKEMON_TYPE_ELECTRIC" : 0xFED248,
        "POKEMON_TYPE_PSYCHIC"  : 0xFC7669,
        "POKEMON_TYPE_ICE"      : 0x6FDDD3,
        "POKEMON_TYPE_DRAGON"   : 0x1A61A8,
        "POKEMON_TYPE_DARK"     : 0x464658,
        "POKEMON_TYPE_FAIRY"    : 0xF193D7
    }

    templateId = StringField(required=True)
    name = StringField(required=True, max_length=10)
    typeIndex = DictField()

    defenseTypeIndex = DictField()

    def icon(self):
        return "http://images.whiskeypicklewolfpack.club/images/type/" + self.name.lower() + ".png"

    def color(self):
        return Type.type_colors[self.templateId]

    def setTypeMap(self, attackScalars):
        for index, scalar in enumerate(attackScalars):
            type_name = Type.type_order[index]
            self.typeIndex[type_name] = scalar

    def setDefenseType(self, type, scalar):
        self.defenseTypeIndex[type] = scalar


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
    damageWindowStart = IntField()
    damageWindowEnd = IntField()
    energyDelta = IntField()
    staminaLossScalar = FloatField()

    def steps(self):
        return math.floor(-100/self.energyDelta)

    def dpe(self, stabMoves=None, weather=None):
        power = self.power

        if power is None:
            power = 0

        if stabMoves is not None and self in stabMoves:
            power = power * 1.2

        if weather is not None and self.type in weather.typeBoost:
            power = power * 1.2

        # energy = self.energyDelta
        #
        # if self.charge:
        #     energy += 500

        return round(power*self.steps(), 1)

    def dps(self, stabMoves=None, weather=None):
        power = self.power

        if power is None:
            power = 0

        if stabMoves is not None and self in stabMoves:
            power = power * 1.2

        if weather is not None and self.type in weather.typeBoost:
            power = power * 1.2

        duration = self.durationMS

        if self.charge:
            duration += 500

        return round((power * 1000)/duration, 1)

class PokemonGender(EmbeddedDocument):
    male = FloatField()
    female = FloatField()

# class PokemonEvolution(Document):


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
    generation = IntField()

    source = StringField()
    name = StringField(required=True)
    description = StringField()
    category = StringField()

    weight = FloatField()
    height = FloatField()
    weightStdDev = FloatField()
    heightStdDev = FloatField()

    type = ReferenceField(Type)
    type2 = ReferenceField(Type)

    baseAttack = IntField()
    baseDefense = IntField()
    baseStamina = IntField()

    quickMoves = ListField(ReferenceField(Move))
    chargeMoves = ListField(ReferenceField(Move))
    stabMoves = ListField(ReferenceField(Move))
    legacyMoves = ListField(ReferenceField(Move))

    familyName = StringField()
    evolutions = ListField(ReferenceField('self'))
    evolvesFrom = ListField(ReferenceField('self'))

    gender = EmbeddedDocumentField(PokemonGender)

    varieties = ListField(StringField())

    rarity = StringField()

    candyToEvolve = IntField()
    baseCatchRate = FloatField()
    baseFleeRate = FloatField()
    buddyDistance = FloatField()

    isBaby = BooleanField()
    hasShiny = BooleanField()

    def generationStr(self):
        gen = self.generation
        genString = "I"
        if gen == 1:
            genString = "I"
        elif gen == 2:
            genString = "II"
        elif gen == 3:
            genString = "III"
        elif gen == 4:
            genString = "IV"
        elif gen == 5:
            genString = "V"
        elif gen == 6:
            genString = "VI"
        elif gen == 7:
            genString = "VII"

        return genString

    def sizeString(self):
        return "{}kg / {}m".format(self.weight, self.height)
    
    def typeString(self):
        typeString = self.type.name

        if self.type2 is not None:
            typeString = "{} / {}".format(self.type.name, self.type2.name)

        return typeString

    def statString(self):
         return "{} / {} / {}".format(self.baseAttack, self.baseDefense, self.baseStamina)

    def raidCPString(self, levels: [int]):
        separator = " / "

        levelsList = []
        for level in levels:
            cp_string = "{} - {}".format(str(self.cp(level, 10, 10, 10)), str(self.cp(level, 15, 15, 15)))
            levelsList.append(cp_string)

        return separator.join(levelsList)

    def cpString(self, levels: [int]):
        separator = " / "

        levelsList = []
        for level in levels:
            cp_string = "{} - {}".format(str(self.cp(level, 0, 0, 0)), str(self.cp(level, 15, 15, 15)))
            levelsList.append(cp_string)

        return separator.join(levelsList)

    def icon(self):
        name = self.name.lower()

        # return "http://images.whiskeypicklewolfpack.club/images/pokesprites/{}.gif".format(name)

        number = str(self.number).zfill(3)

        if self.source == "pokeapi":
            return "https://serebii.net/sunmoon/pokemon/" + number + ".png";
        else:
            return "https://serebii.net/pokemongo/pokemon/" + number + ".png";

    def cp(self, level, attackIV: int, defenseIV: int, staminaIV: int):
        # CP = (Attack * Defense^0.5 * Stamina^0.5 * CP_Multiplier^2) / 10
        attack = self.baseAttack + attackIV
        defense = self.baseDefense + defenseIV
        stamina = self.baseStamina + staminaIV

        return math.floor(((attack) * math.pow(defense, 0.5) * math.pow(stamina, 0.5) * math.pow(Pokemon.cpm_map[str(level)], 2))/10)

    def attack(self, level, iv):
        # Attack=(BaseAttack+AttackIV)∗CpM
        return round((self.baseAttack + iv) * Pokemon.cpm_map[str(level)])

    def defense(self, level, iv):
        # Defense=(BaseDefense+DefenseIV)∗CpM
        return round((self.baseDefense + iv) * Pokemon.cpm_map[str(level)])

    def hp(self, level, iv):
        # HP=Floor((BaseStamina+StaminaIV)∗CpM)
        return math.floor((self.baseStamina + iv) * Pokemon.cpm_map[str(level)])