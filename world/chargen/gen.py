"""
Holds entire character generation process using evennia menus
"""
import operator
import copy
import numpy as np

from evennia.utils.evform import EvForm, EvTable
from evennia.contrib.dice import roll_dice
from world.characteristics import CHARACTERISTICS
from world.birthsigns import *
from world.races import PLAYABLE_RACES, change_race, get_race
from world.gender import ALL_GENDERS
from world.attributes import Attribute


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
    race_stats = copy.deepcopy(get_race(kwargs['race']).stats)

    stat_keys = dict({x.short: x.base for x in race_stats})

    dice = np.vectorize(lambda x: x + roll_dice(1, 8))

    stats = (dice(np.full((7, ), fill_value=0, dtype=np.int64)) +
             list(stat_keys.values())).tolist()
    stat_keys = dict(zip(stat_keys.keys(), stats))

    race_base = dict({x.short: x.base for x in race_stats})

    # return None, None
    form = EvForm('resources.forms.chargen_attribute_roll')
    map = {}
    cntr = 1

    _max = max(stat_keys.items(), key=operator.itemgetter(1))[0]
    _min = min(stat_keys.items(), key=operator.itemgetter(1))[0]
    caller.debug_msg(_min, _max)
    for name, base in race_base.items():
        new_stat = stat_keys[name]

        if name == _max:
            new_stat = f"|g{new_stat}|n"
        if name == _min:
            new_stat = f"|r{new_stat}|n"

        map[cntr] = new_stat
        map[cntr + 1] = base
        cntr += 2
        # text += f"{name.capitalize()}: {stat_keys[name]} ({base})\n"
    form.map(cells=map)
    text = str(form)

    lck = roll_dice(3, 5)
    stat_keys['lck'] = lck
    k = kwargs.copy()
    k['stats'] = stat_keys.copy()
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