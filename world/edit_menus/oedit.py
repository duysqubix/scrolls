"""
Main EvMenu that handles editing objects
"""
import copy
from evennia import GLOBAL_SCRIPTS
from evennia.utils.utils import dedent

_DEFAULT_OBJ_STRUCT = {
    'key': "|yan unfinshed object|n",
    'sdesc': "|yan unfinshed object|n",
    'ldesc': "|yan unfinished object is lying here|n",
    "adesc": None,  # action desciption, message string announced when used
    "type": None,  # type of object: book, weapon, equipment, scroll, etc...
    "wear_flags": None,  #take, head, armor, wield, shield, etc..
    "weight": 0,
    "cost": 0,
    "level": 0,  # minimum level that can use this object
    "applies":
    []  # temporarily changes stats, attrs, and conditions while using
}

_objdb = GLOBAL_SCRIPTS.objdb.vnum


def main_menu(caller):
    obj = caller.ndb._evmenu.obj = {}
    vnum = caller.ndb._evmenu.vnum

    if vnum in _objdb.keys():
        obj = dict(_objdb[vnum])

        # handle missing fields here
        for field, value in _DEFAULT_OBJ_STRUCT.items():
            if field not in obj.keys():
                obj[field] = value
    else:
        obj = copy.deepcopy(_DEFAULT_OBJ_STRUCT)

    text = dedent(f"""
    VNUM : [|W{vnum}|n]
    1) Key          : {obj['key']}
    2) S-Desc.......: {obj['sdesc']}
    3) L-Desc       :- 
    {obj['ldesc']}
    
    4) A-Desc.......: {obj['adesc']}
    5) Type         : {obj['type']} 
    6) Wear Flags...: {obj['wear_flags']}
    7) Weight       : {obj['weight']}
    8) Cost.........: {obj['cost']}
    9) Level        : {obj['level']}
    A) Applies......: {", ".join(obj['applies'])}
    """)

    options = (
        {
            'key': ('', '1'),
            'goto': 'set_keywords'
        },
        {
            'key': ('', '2'),
            'goto': 'set_sdesc'
        },
        {
            'key': ('', '3'),
            'goto': 'set_ldesc'
        },
        {
            'key': ('', '4'),
            'goto': 'set_adesc'
        },
        {
            'key': ('', '5'),
            'goto': 'set_type'
        },
        {
            'key': ('', '6'),
            'goto': 'set_wear_flags'
        },
        {
            'key': ('', '7'),
            'goto': 'set_weight'
        },
        {
            'key': ('', '8'),
            'goto': 'set_cost'
        },
        {
            'key': ('', '9'),
            'goto': 'set_level'
        },
        {
            'key': ('', 'A'),
            'goto': 'set_applies'
        },
    )

    return text, tuple(options)
