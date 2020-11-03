"""
Holds entire character generation process using evennia menus
"""
import random
from evennia import GLOBAL_SCRIPTS
from evennia.utils import utils
from evennia.contrib.dice import roll_dice
from world.characteristics import CHARACTERISTICS

__racesdb = GLOBAL_SCRIPTS.racesdb

def pick_race(caller, **kwargs):
    races = list(__racesdb.db.races.keys())
    text = "Pick a race"
    options = []
    for race in races:
        options.append({
            'key': race,
            'desc': __racesdb.db.races[race]['sdesc'].capitalize(),
            'goto': f"pick_race_{race}"
        })

    return text, tuple(options)


def pick_race_altmer(caller, **kwargs):
    altmer = __racesdb.db.races['altmer']

    desc = altmer['desc']
    stats = altmer['base_stats']
    stats = " ".join([f"{k}:{v}, " for (k, v) in stats.items()])

    text = ("Altmer or high elves (Help for more information)" \
    f"\n{stats}", utils.wrap(desc, 80))
    options = ({
        'key': 'yes',
        'desc': "Do you want to be an altmer",
        'goto': ("altmer_novice_skill_upgrade", {'race': 'altmer'})
    }, {
        'key': 'no',
        'desc': 'pick another race',
        'goto': "pick_race"
    })
    return text, options

def altmer_novice_skill_upgrade(call, **kwargs):
    text = "You can decide on one of the following to start as a novice"
    options = []
    for skill in ['alchemy', 'alteration', 'conjuratin', 'destruction', 'enchanting', 'illusion', 'mysticism', 'restoration']:
        k = kwargs.copy()
        k['novice'] = skill
        options.append({
            'key': skill,
            'goto': ('gen_characteristics_1', k)
        })
    return text, tuple(options)

def pick_birthsign(caller, **kwargs):
    pass

def gen_characteristics_1(caller, **kwargs):
    text = "Choose a favored characteristic"
    options = []
    for stat in CHARACTERISTICS:
        k = kwargs.copy()
        k['favored_stat_1'] = stat.short
        options.append({
            'key': stat.short,
            'goto': ('gen_characteristics_2', k)
        })
    return text, tuple(options)


def gen_characteristics_2(caller, **kwargs):
    text = "Choose another favored characteristic"
    options = []

    for stat in [x for x in CHARACTERISTICS if x.short != kwargs['favored_stat_1']]:
        k = kwargs.copy()
        k['favored_stat_2'] = stat.short
        options.append({
            'key': stat.short,
            'goto': ('gen_characteristics_3', k)
        })
    return text, tuple(options)

def gen_characteristics_3(caller, **kwargs):
    caller.msg(kwargs)
    stats = dict(__racesdb.db.races[kwargs['race']]['base_stats'])
    stat_keys = list(stats.keys())
    for _ in range(7):
        k1 = random.choice(stat_keys)
        k2 = random.choice(stat_keys)
        _,_,_,(roll1, roll2) = roll_dice(2,10, return_tuple=True)
        stats[k1] += roll1
        stats[k2] += roll2
    
    text = f"Roll for stats\n{stats}"
    lck = roll_dice(2,10, ('+', 30))
    if lck > 50:
        lck = 50
    stats['lck'] = lck
    k = kwargs.copy()
    k['stats'] = stats.copy()
    options = ({
        'key': 'accept',
        'goto': ('gen_characteristics_4',k)
    },{
        'key': 'reroll',
        'goto': ('gen_characteristics_3', k)
    })
    return text, options