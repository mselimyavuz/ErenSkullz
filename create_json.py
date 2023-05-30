import json
import csv
import random
import os
import global_var as gv
'''
with open('collection.csv', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    next(csv_reader)
    collection = []

    for row in csv_reader:
        collection.append({'Collection': row[0], 'SkullzID': row[1], 'rarity': row[2], 'Image': row[3]})

with open('current_squads.json', 'w') as file:
    col_list = []
    for item in collection[:6]:
        col_list.append({'skullz': f"{item['Collection']}_{item['SkullzID']}", 'squad':  1})
    for item in collection[6:12]:
        col_list.append({'skullz': f"{item['Collection']}_{item['SkullzID']}", 'squad':  2})
    for item in collection[12:18]:
        col_list.append({'skullz': f"{item['Collection']}_{item['SkullzID']}", 'squad':  3})
    json.dump(col_list, file)
'''

values = {'AVAX': gv.AVAX, 'DAYS': gv.DAYS, 'FLSH': gv.FLSH, 'RFLSH': gv.RFLSH, 'WD_COST': gv.WD_COST}

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "current_values.json")
with open(file_path, 'w') as file:
    json.dump(values, file)

