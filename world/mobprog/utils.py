"""
mobprog valid functions
"""
import random
from world.utils.utils import is_npc, is_pc


def ispc(obj):
    return is_pc(obj)


def isnpc(obj):
    return is_npc(obj)


def level(obj):
    if obj.attributes.has('attrs'):  # npc/pc
        return obj.attrs.level.value
    elif obj.attributes.has('level'):  # object
        return obj.db.level


def is_immort(obj):
    if level(obj) > 200:
        return True
    return False


def rand(num):
    return random.randint(0, 100) <= num
