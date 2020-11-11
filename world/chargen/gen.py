"""
Holds entire character generation process using evennia menus
"""
import random
from evennia import GLOBAL_SCRIPTS
from evennia.utils import utils
from evennia.contrib.dice import roll_dice
from world.characteristics import CHARACTERISTICS
from world.birthsigns import *
from world.races import PLAYABLE_RACES, get_race
from world.attributes import Attribute
import copy


def pick_race(caller, **kwargs):
    races = [(x.name, x.sdesc) for x in PLAYABLE_RACES]
    text = "Pick a race"
    options = []
    for name, sdesc in races:
        options.append({
            'key': name.capitalize(),
            'desc': f"|c{sdesc.capitalize()}|n",
            'goto': (f"pick_race_specific", {
                'race': name
            })
        })

    return text, tuple(options)


def pick_race_specific(caller, **kwargs):
    race = get_race(kwargs['race'])
    desc = race.desc
    stats = race.stats
    stats = " ".join([f"{stat.short}:{stat.base}, " for stat in stats])

    text = ("(Help for more information)" \
    f"\n{stats}", utils.wrap(utils.dedent(desc), 80))
    options = ({
        'key':
        'yes',
        'desc':
        f"Do you want to be an {kwargs['race']}",
        'goto': ("altmer_novice_skill_upgrade", {
            'race': f"{kwargs['race']}"
        })
    }, {
        'key': 'no',
        'desc': 'pick another race',
        'goto': "pick_race"
    })
    return text, options


def altmer_novice_skill_upgrade(call, **kwargs):
    text = "You can decide on one of the following to start as a novice"
    options = []
    for skill in [
            'alchemy', 'alteration', 'conjuratin', 'destruction', 'enchanting',
            'illusion', 'mysticism', 'restoration'
    ]:
        k = kwargs.copy()
        k['skill'] = {skill: 'novice'}
        options.append({'key': skill, 'goto': ('gen_characteristics_1', k)})
    return text, tuple(options)


def gen_characteristics_1(caller, **kwargs):
    text = "Choose a favored characteristic"
    options = []
    for stat in CHARACTERISTICS.values():
        k = kwargs.copy()
        k['favored_stats'] = [stat.short]
        options.append({
            'key': stat.short,
            'goto': ('gen_characteristics_2', k)
        })
    return text, tuple(options)


def gen_characteristics_2(caller, **kwargs):
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
            'key': stat.short,
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

    text = f"Roll for stats\n{stat_keys}"
    lck = roll_dice(2, 10, ('+', 30))
    if lck > 50:
        lck = 50
    stat_keys['lck'] = lck
    k = kwargs.copy()
    k['stats'] = stat_keys.copy()
    options = ({
        'key': 'accept',
        'goto': ('determine_birthsign', k)
    }, {
        'key': 'reroll',
        'goto': ('gen_characteristics_3', k)
    })
    return text, options


def determine_birthsign(caller, **kwargs):
    text = "Determine your birthsign"

    options = []
    for sign in ['warrior', 'mage', 'thief']:
        k = kwargs.copy()
        k['birthsign'] = {'name': sign}
        options.append({'key': sign, 'goto': ('finish', k)})
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
    thief_signs = []
    if kwargs['birthsign']['name'] == 'warrior':
        kwargs['birthsign']['sign'] = warrior_signs[idx](is_cursed)

    elif kwargs['birthsign']['name'] == 'mage':
        kwargs['birthsign']['sign'] = mage_signs[idx](is_cursed)

    # change birthsign
    change_birthsign(caller, kwargs['birthsign']['sign'])
    # set race
    race = copy.deepcopy(get_race(kwargs['race']))
    caller.attrs.race = Attribute(race.name, race)
    caller.msg(kwargs)
    # caller.save()
    return None, None