"""
Holds entire character generation process using evennia menus
"""
import random
import copy
from world.attributes import Attribute
import numpy as np
from evennia import GLOBAL_SCRIPTS
from evennia.contrib.dice import roll_dice
from world.characteristics import CHARACTERISTICS
from world.birthsigns import *
from world.races import PLAYABLE_RACES, change_race, get_race
from world.gender import ALL_GENDERS
from evennia.utils.evform import EvForm, EvTable


def pick_race(caller, **kwargs):
    races = [(x.name, x.sdesc) for x in PLAYABLE_RACES]
    text = "Pick a race"
    form = EvForm('resources.chargen_race_form')

    race_info = np.zeros((len(PLAYABLE_RACES), 8), dtype='object')

    for idx in range(len(PLAYABLE_RACES)):

        info = []
        s = PLAYABLE_RACES[idx]
        name = s.name.capitalize()
        for idy in range(8):
            if idy == 0:
                info.append(name)
            else:
                info.append(s.stats[idy - 1].base)

        max = np.max([x for x in info if isinstance(x, int)])
        min = np.min([x for x in info if isinstance(x, int)])

        idx_max = info.index(max)
        idx_min = info.index(min)
        info[idx_max] = f"|g{info[idx_max]}|n"
        info[idx_min] = f"|r{info[idx_min]}|n"

        info = [str(x) for x in info]
        race_info[idx] = info

    race_table = EvTable("Race",
                         "Str",
                         "End",
                         "Agi",
                         "Int",
                         "Wp",
                         "Prc",
                         "Prs",
                         table=race_info.transpose().tolist(),
                         border='incols',
                         height=2)
    form.map(tables={'B': race_table})
    text = str(form) + "\n*base stats"

    options = []
    for name, sdesc in races:
        options.append({
            'key': name.capitalize(),
            'desc': f"|c{sdesc.capitalize()}|n",
            'goto': ("skill_upgrade", {
                'race': name
            })
        })

    return text, tuple(options)


def skill_upgrade(caller, **kwargs):
    race = get_race(kwargs['race'])
    text = "Choose a skill to upgrade to novice for free"
    options = []

    if not race.upgradable_skills:
        k = kwargs.copy()
        k['upgraded_skill'] = None
        text, options = "Press `enter` to continue", ({
            'key':
            '_default',
            'goto': ('favored_characteristics_1', k)
        })
        return text, options

    for skill in race.upgradable_skills:
        k = kwargs.copy()
        k['upgraded_skill'] = {skill: 'novice'}
        options.append({
            'key': skill,
            'goto': ('favored_characteristics_1', k)
        })
    return text, tuple(options)


def favored_characteristics_1(caller, **kwargs):
    text = "Choose a favored characteristic"
    options = []
    for stat in CHARACTERISTICS.values():
        k = kwargs.copy()
        k['favored_stats'] = [stat.short]
        options.append({
            'key': stat.name.capitalize(),
            'goto': ('favored_characteristics_2', k)
        })
    return text, tuple(options)


def favored_characteristics_2(caller, **kwargs):
    text = "Choose another favored characteristic"
    options = []

    for stat in [
            x for x in CHARACTERISTICS.values()
            if x.short not in kwargs['favored_stats']
    ]:
        k = kwargs.copy()
        k['favored_stats'] = k['favored_stats'].copy()
        k['favored_stats'].append(stat.short)
        options.append({
            'key': stat.name.capitalize(),
            'goto': ('gen_characteristics_3', k)
        })
    return text, tuple(options)


def gen_characteristics_3(caller, **kwargs):
    stats = copy.deepcopy(get_race(kwargs['race']).stats)
    stat_keys = dict({x.short: x.base for x in stats})
    for _ in range(7):
        k1 = random.choice(list(stat_keys.keys()))
        k2 = random.choice(list(stat_keys.keys()))
        _, _, _, (roll1, roll2) = roll_dice(2, 10, return_tuple=True)
        stat_keys[k1] += roll1
        stat_keys[k2] += roll2

    race_base = dict({x.short: x.base for x in stats})

    text = "Roll for stats (enter for reroll)\n\n"

    lck = roll_dice(2, 10, ('+', 30))
    if lck > 50:
        lck = 50
    stat_keys['lck'] = lck
    k = kwargs.copy()
    k['stats'] = stat_keys.copy()

    _max = max(stat_keys.keys(), key=(lambda key: stat_keys[key]))
    _min = min(stat_keys.keys(), key=(lambda key: stat_keys[key]))

    stat_keys[_max] = f"|g{stat_keys[_max]}|n"
    stat_keys[_min] = f"|r{stat_keys[_min]}|n"

    for name, base in race_base.items():
        text += f"{name.capitalize():>3}: {stat_keys[name]} ({base})\n"

    options = ({
        'key': 'accept',
        'goto': ('determine_birthsign', k)
    }, {
        'key': '_default',
        'goto': ('gen_characteristics_3', k)
    })
    return text, options


def determine_birthsign(caller, **kwargs):
    text = "Determine your fate"

    options = []
    for sign in ['warrior', 'mage', 'thief']:
        k = kwargs.copy()
        k['birthsign'] = {'name': sign}
        options.append({
            'key': sign.capitalize(),
            'goto': ('decide_gender', k)
        })
    return text, tuple(options)


def decide_gender(caller, **kwargs):
    text = "Select your gender"

    options = []
    for gender in ALL_GENDERS:
        k = kwargs.copy()
        k['gender'] = gender
        options.append({
            'key': gender.value.capitalize(),
            'goto': ("finish", k)
        })

    return text, tuple(options)


def finish(caller, **kwargs):

    # set base stats
    for stat, base in kwargs['stats'].items():
        _s = caller.stats.get(stat)
        _s.base = base
        caller.stats.set(stat, _s)

    # calc_birthsign and assign
    is_cursed = False
    idx = None
    while 1:
        idx = roll_dice(1, 5) - 1
        if idx < 4:
            break
        is_cursed = True

    warrior_signs = [WarriorSign, LadySign, SteedSign, LordSign]
    mage_signs = [MageSign, ApprenticeSign, AtronachSign, RitualSign]
    thief_signs = [ThiefSign, LoverSign, ShadowSign, TowerSign]
    if kwargs['birthsign']['name'] == 'warrior':
        kwargs['birthsign']['sign'] = warrior_signs[idx](is_cursed)

    elif kwargs['birthsign']['name'] == 'mage':
        kwargs['birthsign']['sign'] = mage_signs[idx](is_cursed)

    elif kwargs['birthsign']['name'] == 'thief':
        kwargs['birthsign']['sign'] = thief_signs[idx](is_cursed)

    # change birthsign
    change_birthsign(caller, kwargs['birthsign']['sign'])
    # set race
    race = copy.deepcopy(get_race(kwargs['race']))
    change_race(caller, race)

    # set gender
    caller.attrs.gender = Attribute('gender', kwargs['gender'])

    # caller.msg(kwargs)
    caller.attrs.update()
    caller.full_restore()
    return None, None