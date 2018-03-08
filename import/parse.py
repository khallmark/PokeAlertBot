#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from collections import OrderedDict

masterNew = json.load(open('game_master/versions/latest/GAME_MASTER.json'), object_pairs_hook=OrderedDict)

masterNewIn = masterNew['itemTemplates']

docs = 'avatars', 'badges', 'settings', 'forms', 'items', 'types', 'quests', 'spawns', 'pokemons', 'moves', 'cameras', 'iaps', 'sequences', 'missed', 'weather'
generalNew = OrderedDict()
suffixNew = ''

directory = '../output/'
indent = 2

if not os.path.exists(directory):
    os.makedirs(directory)


def opener(document, suffix):
    content = open(directory + document + suffix + '.json', 'w')
    return content


def start(general):
    for doc in docs:
        general[doc] = {'name': doc, 'items': []}


def parse(json_file, general):
    for a in json_file:
        if a['templateId'].startswith('AVATAR_'):
            general['avatars']['items'].append(a)
        elif a['templateId'].startswith('BADGE_'):
            general['badges']['items'].append(a)
        elif a['templateId'].endswith('_SETTINGS'):
            general['settings']['items'].append(a)
        elif a['templateId'].startswith('FORMS_'):
            general['forms']['items'].append(a)
        elif a['templateId'].startswith('ITEM_'):
            general['items']['items'].append(a)
        elif a['templateId'].startswith('POKEMON_TYPE_'):
            general['types']['items'].append(a)
        elif a['templateId'].startswith('QUEST_'):
            general['quests']['items'].append(a)
        elif a['templateId'].startswith('SPAWN_'):
            general['spawns']['items'].append(a)
        elif a['templateId'].startswith('_MOVE_', 5):
            general['moves']['items'].append(a)
        elif a['templateId'].startswith('_POKEMON_', 5):
            general['pokemons']['items'].append(a)
        elif a['templateId'].startswith('camera_'):
            general['cameras']['items'].append(a)
        elif 'iapItemDisplay' in a and a['iapItemDisplay']['category'].startswith('IAP_'):
            general['iaps']['items'].append(a)
        elif a['templateId'].startswith('sequence_'):
            general['sequences']['items'].append(a)
        elif a['templateId'].startswith('WEATHER_'):
            general['weather']['items'].append(a)
        else:
            general['missed']['items'].append(a)
            # print "This one fled: " + str(a)


def write(general, suffix):
    for category in docs:
        doc = opener(category, suffix)
        for i, item in enumerate(general[category]['items']):
            if i == 0:
                doc.write('[' + str(json.dumps(item, indent=indent)) + ', ')
            elif i == len(general[category]['items']) - 1:
                doc.write(str(json.dumps(item, indent=indent)) + ']')
            else:
                doc.write(str(json.dumps(item, indent=indent)) + ', ')


start(generalNew)
parse(masterNewIn, generalNew)
write(generalNew, suffixNew)