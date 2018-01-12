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
    type = StringField()

class Pokemon(Document):
    templateId = StringField(required=True)
    number = IntField()
    name = StringField(required=True)
    type = ReferenceField(Type)
    type2 = ReferenceField(Type)
    baseAttack = IntField()
    baseDefense = IntField()
    baseStamina = IntField()
    # quickMoves = ListField()
    # chargeMoves = ListField()
    # familyId = StringField()