from mongoengine import *

class Type(Document):
    templateId = StringField(required=True)
    name = StringField(required=True, max_length=10)
    type_map = DictField()

class Weather(Document):
    templateId = StringField(required=True)
    name = StringField(required=True)
    type_boost = ListField(ReferenceField(Type))

class Move(Document):
    templateId = StringField(required=True)
    name = StringField()
    type = StringField()

class Pokemon(Document):
    templateId = StringField(required=True)
    name = StringField(required=True)
    type = ReferenceField(Type)
    type2 = ReferenceField(Type)
    baseAttack = IntField()
    baseDefense = IntField()
    baseStamina = IntField()
    # quickMoves = ListField()
    # chargeMoves = ListField()
    # familyId = StringField()