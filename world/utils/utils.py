from evennia.utils.utils import inherits_from
from world.conditions import Hidden, Invisible
from evennia.utils import make_iter


def highlight_words(block, key_targets, color_codes):
    key_targets = make_iter(key_targets)
    color_codes = make_iter(color_codes)

    if len(key_targets) != len(color_codes):
        raise ValueError("target words and color codes must match 1:1")

    for idx, key in enumerate(key_targets):
        block.replace(key, f"{color_codes[idx]}{key}|n")
    return block


def is_pc(caller):
    """ checks to see if caller is pc """
    if not caller.db.is_pc:
        return False
    return caller.db.is_pc


def is_npc(caller):
    """ checks to see if caller is npc """
    if not caller.db.is_npc:
        return True
    return caller.db.is_npc


def is_invis(caller):
    """
    checks if caller has invisible condition
    """

    if not is_npc(caller) or not is_pc(caller):
        return False

    return caller.conditions.has(Invisible)


def is_hidden(caller):
    """ checks if caller is hidden """
    if not is_npc(caller) and not is_pc(caller):
        return False

    return caller.conditions.has(Hidden)


def is_obj(obj):
    """checks if caller inherits scrolls object"""
    return inherits_from(obj,
                         'typeclasses.objs.object.Object') and obj.db.is_obj


def is_equipment(obj):
    """ checks if obj is of equipment type"""
    return is_obj(obj) and obj.__obj_type__ == 'equipment'


def is_weapon(obj):
    """ checks if obj is of weapon type"""
    return is_obj(obj) and obj.__obj_type__ == 'weapon'


def can_pickup(caller, obj):
    """ tests whether obj can be picked up based on caller """
    if obj.db.level > caller.attrs.level.value:
        return False

    return True


def is_equippable(obj):
    """
    tests whether obj can be equipped or not
    """
    # both these attributes are unique and is not set to None
    # on Equipment Objects
    return is_equipment(obj) and obj.db.equippable


def is_wieldable(obj):
    """ tests if obj is a weapon and wieldable"""
    return is_weapon(obj) and obj.db.wieldable


def is_wielded(obj):
    if not is_weapon(obj):
        return False
    return obj.db.is_wielded


def is_worn(obj):
    """ tests if object is currently set as worn"""
    if not is_equipment(obj):
        return False
    return obj.db.is_worn


def is_cursed(obj):
    """ check to see if object can be removed"""
    return False  #TODO: Implement is_cursed()
