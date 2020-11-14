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