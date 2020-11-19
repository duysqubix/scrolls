from world.globals import BUILDER_LVL
from evennia.utils.utils import inherits_from
from world.conditions import DetectHidden, DetectInvis, Hidden, Invisible
from evennia.utils import make_iter


def highlight_words(block, key_targets, color_codes):
    key_targets = make_iter(key_targets)
    color_codes = make_iter(color_codes)

    if len(key_targets) != len(color_codes):
        raise ValueError("target words and color codes must match 1:1")

    for idx, key in enumerate(key_targets):
        block.replace(key, f"{color_codes[idx]}{key}|n")
    return block


def is_wiz(caller):
    """ checks to see if player is immortal """
    if not is_npc(caller) or not is_pc(caller):
        return False

    if caller.attrs.level.value <= BUILDER_LVL:
        return False
    return True


def is_pc(caller):
    """ checks to see if caller is pc """
    if not caller.db.is_pc:
        return False
    return caller.db.is_pc


def is_npc(caller):
    """ checks to see if caller is npc """
    if not caller.db.is_npc:
        return False
    return caller.db.is_npc


def is_invis(caller):
    """
    checks if caller has invisible condition
    caller could be pc/npc/or obj
    """

    if is_obj(caller):
        return "invis" in caller.db.tags

    if not is_npc(caller) or not is_pc(caller):
        return False

    return caller.conditions.has(Invisible)


def can_see(target, vict):
    """
    first argument must be a pc/npc character
    second argument can either be obj or pc/npc
    """

    if not is_pc(target) and not is_npc(target):
        return False

    if is_pc(vict) or is_npc(vict):
        # check here for pc 2 pc if they can see each other

        if not target.conditions.has(DetectInvis) and is_invis(vict):
            return False
        elif not target.conditions.has(DetectHidden) and is_hidden(vict):
            return False
        else:
            return True

    if not is_obj(vict):
        return False

    if not is_invis(vict):
        return True
    else:
        if not target.conditions.has(DetectInvis) and is_invis(vict):
            return False
        else:
            return True


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
    """ tests if object is currently set as worn """
    if not is_equipment(obj):
        return False
    return obj.db.is_worn


def is_equipped(obj):
    """ checks to see if obj is worn or wielded"""
    if not is_obj(obj):
        return False
    return is_wielded(obj) or is_worn(obj)


def is_cursed(obj):
    """ check to see if object can be removed"""
    return 'cursed' in obj.db.tags
