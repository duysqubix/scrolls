from json import JSONEncoder
import numpy as np
import random
import re
from functools import reduce
from numpy.lib.arraysetops import isin
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from evennia import GLOBAL_SCRIPTS, create_object
from evennia.contrib.rplanguage import obfuscate_language
from evennia.utils import make_iter
from evennia.utils.utils import inherits_from, string_partial_matching

from typeclasses.objs.object import VALID_OBJ_APPLIES
from typeclasses.objs.custom import CUSTOM_OBJS
from world.globals import BUILDER_LVL, BOOK_CATEGORIES
from world.utils.db import search_objdb, search_mobdb
from world.conditions import DetectHidden, DetectInvis, Hidden, HolyLight, Invisible, Sleeping, get_condition

_CAP_PATTERN = re.compile(r'((?<=[\.\?!\n]\s)(\w+)|(^\w+))')
_LANG_TAGS = re.compile('\>(.*?)\<', re.I)


class DBDumpEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            super().default(obj)


class EntityLoader:
    """
    handels dynamically loading entities, the caller of this class
    should be location
    """
    def __init__(self, caller, parent, children, amount=1):
        self.type, self.vnum = parent.split(' ')
        self.caller = caller
        self.amount = amount
        _children_list = []
        if children:
            for child in children:
                type_, vnum = child.split(' ')
                _children_list.append([type_, vnum])
        self.children = _children_list

        if self.type == 'mob':
            self.name = search_mobdb(vnum=int(self.vnum))[0]['sdesc']
        elif self.type == 'obj':
            self.name = search_objdb(vnum=int(self.vnum))[0]['sdesc']
        else:
            self.name = "not implemented"

    def children_names(self):
        names = []
        n = " (|r{vnum}|n) {name}"
        for type_, vnum in self.children:
            vnum = int(vnum)
            if type_ == 'mob':
                name = search_mobdb(vnum=vnum)[0]['sdesc']
                names.append(n.format(name, vnum))

            elif type_ == 'obj':
                name = search_objdb(vnum=vnum)[0]['sdesc']
                names.append(n.format(name=name, vnum=vnum))

        return names

    def load(self):

        for _ in range(self.amount):
            if self.type == 'mob':
                mob = create_object("typeclasses.mobs.mob.Mob", key=self.vnum)
                for ctype, cvnum in self.children:
                    if ctype != 'obj':
                        continue
                    obj_bp = search_objdb(vnum=cvnum)
                    if not obj_bp:
                        continue
                    obj_bp = obj_bp[0]
                    obj = create_object(CUSTOM_OBJS[obj_bp['type']],
                                        key=int(cvnum))
                    obj.move_to(mob, quiet=True)

                mob.move_to(self.caller, quiet=True)

            elif self.type == 'obj':
                obj_bp = search_objdb(vnum=self.vnum)
                if not obj_bp:
                    return
                obj_bp = obj_bp[0]
                obj = create_object(CUSTOM_OBJS[obj_bp['type']],
                                    key=int(self.vnum))

                for ctype, cvnum in self.children:
                    if ctype != 'obj':
                        continue
                    obj_bp = search_objdb(vnum=cvnum)
                    if not obj_bp:
                        continue
                    obj_bp = obj_bp[0]
                    obji = create_object(CUSTOM_OBJS[obj_bp['type']],
                                         key=int(cvnum))
                    obji.move_to(obj, quiet=True)

                obj.move_to(self.caller, quiet=True)

    def read(caller, yaml_str):
        data = yaml.load(yaml_str, Loader=Loader)
        parsed = []
        for parent, children in data.items():
            amount = 1
            obj = parent.split(' ')
            if len(obj) != 2:
                continue
            if children:
                for child in children:
                    obj = child.split(' ')
                    if len(obj) != 2:
                        continue
                    if obj[0] == 'num':
                        amount = int(obj[1])


#             parsed[parent] = children
            parsed.append(EntityLoader(caller, parent, children,
                                       amount=amount))

        return parsed


def factors(n):
    """
    efficiently find the factors of a given number
    """
    return set(
        reduce(list.__add__, ([i, n // i]
                              for i in range(1,
                                             int(n**0.5) + 1) if n % i == 0)))


def highlight_words(block, key_targets, color_codes):
    key_targets = make_iter(key_targets)
    color_codes = make_iter(color_codes)

    if len(key_targets) != len(color_codes):
        raise ValueError("target words and color codes must match 1:1")

    for idx, key in enumerate(key_targets):
        block.replace(key, f"{color_codes[idx]}{key}|n")
    return block


def capitalize_sentence(string):
    global _CAP_PATTERN
    return _CAP_PATTERN.sub(lambda x: x.group().capitalize(), string)


def rplanguage_parse_string(ch, string):
    """
    Obfuscates string based on keys that set the type of language
    and the skill of the player corresponding to that language.

    ex:
    x = ">aldmerish< This is something only one skilled in aldmerish can read"

    # ch.languages.aldmerish.level == 0.5
    new_string = obfuscate_string(ch, x)

    new_string == "This is eyjhuadh only one yzychy in ygyshy can read"


    *** Important ***
    If you plan on using this function, it is import that string supplied
    must have >[language]< first then contents in order for this function to parse correctly.
    """
    global _LANG_TAGS

    chunks = re.split(_LANG_TAGS, string)[1:]
    if not chunks:
        # no tags found for a language
        return string

    if len(chunks) % 2 != 0:
        raise ValueError("error in regex on rplanguage tag system.")

    tmp = 0
    languages = dict()
    for i in range(0, len(chunks), 2):
        languages[f"{chunks[i]}_{tmp}"] = chunks[i + 1].lstrip()
        tmp += 1

    new_string = []
    for lang, text in languages.items():
        lang = lang.split('_')[0]
        lang_skill = ch.languages.get(lang)
        if not lang_skill:
            # language doesn't exist (tag is wrong or language isn't implemented)
            new_string.append(text)
            continue
        lang_skill = lang_skill.level
        obfuscated_string = obfuscate_language(text,
                                               level=1.0 - lang_skill,
                                               language=lang)
        new_string.append(obfuscated_string)

    translated_string = "".join(new_string)
    #return capitalize_sentence(translated_string)
    return translated_string


def apply_obj_effects(ch, obj):
    """
    apply the loaded effects from obj onto ch
    """
    if not is_pc_npc(ch) or not is_obj(obj):
        return

    # handle any messages here to ch when worn
    if obj.__apply_on_msg__:
        ch.msg(obj.__apply_on_msg__)

    # handle applies (conditions set on items)
    applies = list(obj.db.applies)
    if applies:
        for effect in applies:
            if len(effect) == 2:
                apply_type, mod = effect

                if apply_type in VALID_OBJ_APPLIES['attrs']:
                    ch.attrs.modify_vital(apply_type, by=mod)

                elif apply_type in VALID_OBJ_APPLIES['stats']:
                    ch.stats.modify_stat(apply_type, by=mod)

            if len(effect) == 3:
                condition, x, y = effect
                if condition in VALID_OBJ_APPLIES['conditions']:
                    con = get_condition(condition)
                    ch.conditions.add(con)

    # handle ar,mar set on equipment objects
    if obj.db.type == 'equipment':
        ch.attrs.AR.value += obj.db.extra['AR']
        ch.attrs.MAR.value += obj.db.extra['MAR']


def remove_obj_effects(ch, obj):
    """
    remove the loaded effects from obj onto ch
    """
    if not is_pc_npc(ch) or not is_obj(obj):
        return

    # handle any messages here to ch when worn
    if obj.__apply_off_msg__:
        ch.msg(obj.__apply_off_msg__)

    applies = list(obj.db.applies)
    if applies:

        for effect in applies:
            if len(effect) == 2:
                apply_type, mod = effect
                if apply_type in VALID_OBJ_APPLIES['attrs']:
                    ch.attrs.modify_vital(apply_type, by=-mod)

                elif apply_type in VALID_OBJ_APPLIES['stats']:
                    ch.stats.modify_stat(apply_type, by=-mod)
            if len(effect) == 3:
                condition, x, y = effect
                if condition in VALID_OBJ_APPLIES['conditions']:
                    con = get_condition(condition)
                    ch.conditions.remove(con)
    # handle ar,mar set on equipment objects
    if obj.db.type == 'equipment':
        ch.attrs.AR.value -= obj.db.extra['AR']
        ch.attrs.MAR.value -= obj.db.extra['MAR']


def random_book(caller, category=None):
    """
    returns a random book from the object database
    if category is supplied it will return a random book from that category. The
    book will be loaded and put into callers contents
    """
    if category not in BOOK_CATEGORIES:
        books = search_objdb(type='book')
        rvnum = random.choice([x['vnum'] for x in books])
    else:
        books = search_objdb(type='book', extra=f'category {category}')
        rvnum = random.choice([x['vnum'] for x in books])

    book = create_object('typeclasses.objs.custom.Book', key=rvnum)
    book.move_to(caller)


def mxp_string(key, contents):
    return f"|lc{key}|lt{contents}|le"


def clear_terminal(obj):
    """ clears the clients screen, but ony if client supports it"""
    if not is_pc(obj) or not is_online(obj):
        return
    obj.msg("\u001B[2J")


def next_available_rvnum():
    return max(GLOBAL_SCRIPTS.roomdb.vnum.keys()) + 1


def get_name(obj):
    if is_pc(obj):
        return obj.name

    elif is_npc(obj):
        return obj.db.sdesc

    elif is_obj(obj):
        return obj.db.name


def match_string(criteria, string):
    string = make_iter(string)
    return True if string_partial_matching(string, criteria) else False


def match_name(name, obj):
    name = name.lower()

    matched = False
    if is_obj(obj) and string_partial_matching(obj.db.name, name):
        matched = True

    elif is_pc(obj) and string_partial_matching(make_iter(obj.name.lower()),
                                                name):
        matched = True

    elif is_npc(obj) and string_partial_matching(make_iter(obj.db.key), name):
        matched = True
    return matched


def delete_contents(obj, exclude=[], do_not_delete_chars=True):
    """ 
    DANGEROUS OPERATION

    recursively delete objs contained within itself 
    make sure to put appropriate typeclasses in exclude,
    you can delete yourself if you are not careful..
    for example. 
    
    By default this skips over character typeclasses,
    but this can be overwritten. 

    # bad!!
    delete_contents(self.caller.location, do_not_delete_chars=False) # whoopsie.. doooh

    # good!!
    delete_contents(self.caller.location)
    """

    for o in obj.contents:
        if o in exclude or (do_not_delete_chars and o.db.is_pc):
            continue
        if o.contents:
            delete_contents(obj=o)
        o.delete()


def parse_dot_notation(string):
    """
    Parses dot notation string like so:

    ex: 1.book = (1, 'book')
    ex: all.book = ('all','book')
    ex: book = (None, 'book')
    """
    pos = None
    if "." in string:
        pos, name = string.split('.')
        if pos != 'all':
            pos = int(pos)
        return pos, name
    return pos, string


def room_exists(vnum):
    roomdb = GLOBAL_SCRIPTS.roomdb
    return vnum in roomdb.vnum.keys()


def has_zone(obj):
    """ returns the objs assigned zone, if any """
    return obj.db.assigned_zone


def has_light(ch):
    """ 
    checks to see if npc/pc has a light 
    object equipped
    """
    if not is_pc_npc(ch):
        return False

    if not ch.equipment.location['light']:
        return False
    return True


def is_wiz(obj):
    """ checks to see if player is immortal """

    if not is_pc(obj):
        return False

    if obj.attrs.level.value > BUILDER_LVL:
        return True
    return False


def is_builder(obj):
    """ checks to see if player is a builder """
    if not is_pc(obj):
        return False
    if obj.attrs.level.value >= BUILDER_LVL:
        return True
    return False


def is_online(pc):
    """ checks to see if pc is online and connected to account"""
    return pc.has_account


def is_pc(obj):
    """ checks to see if obj is pc """
    if not obj.db.is_pc:
        return False
    return obj.db.is_pc


def is_npc(obj):
    """ checks to see if obj is npc """
    if not obj.db.is_npc:
        return False
    return obj.db.is_npc


def is_pc_npc(obj):
    """ checks to see if obj is a playable character or mob"""
    return is_pc(obj) or is_npc(obj)


def is_invis(obj):
    """
    checks if obj has invisible condition
    obj could be pc/npc/or obj
    """

    if is_obj(obj):
        return "invis" in obj.db.tags

    if not is_pc_npc(obj):
        return False

    return obj.conditions.has(Invisible)


def can_see_room(target, room=None):
    """checks to see if target can see room"""
    pass


def can_see_obj(target, vict):
    """
    first argument must be a pc/npc character
    second argument can either be obj or pc/npc
    """

    if not is_pc(target) and not is_npc(target):
        return False

    if target.conditions.has(HolyLight):
        return True
    if is_pc_npc(vict):
        # check here for pc 2 pc if they can see each other

        if not target.conditions.has(DetectInvis) and is_invis(vict):
            return False
        elif not target.conditions.has(DetectHidden) and is_hidden(vict):
            return False
        else:
            return True

    if not is_obj(vict):
        return False

    # if we got here, we can be sure that vict is obj
    if not is_invis(vict):
        return True
    else:
        if not target.conditions.has(DetectInvis) and is_invis(vict):
            return False
        else:
            return True


def is_hidden(obj):
    """ checks if obj is hidden """
    if not is_pc_npc(obj):
        return False

    return obj.conditions.has(Hidden)


def is_sleeping(obj):
    """checks to see if obj is sleeping"""
    # only pc and npc can be sleeping
    if not is_pc_npc(obj):
        return False
    if obj.conditions.has(Sleeping):
        return True
    return False


def is_room(obj):
    """checks if obj inherits room object"""
    return inherits_from(obj,
                         'typeclasses.rooms.rooms.Room') and obj.db.is_room


def is_exit(obj):
    """ checks if obj is exit type"""
    return inherits_from(obj, 'typeclasses.exits.Exit') and obj.db.is_exit


def is_obj(obj):
    """checks if obj inherits scrolls object"""
    return inherits_from(obj,
                         'typeclasses.objs.object.Object') and obj.db.is_obj


def is_equipment(obj):
    """ checks if obj is of equipment type"""
    return is_obj(obj) and obj.__obj_type__ == 'equipment'


def is_light(obj):
    """ checks if obj is a light source"""
    return is_obj(obj) and obj.__obj_type__ == 'light'


def is_weapon(obj):
    """ checks if obj is of weapon type"""
    return is_obj(obj) and obj.__obj_type__ == 'weapon'


def is_staff(obj):
    """ checks if obj is of type staff"""
    return is_obj(obj) and obj.__obj_type__ == 'staff'


def is_book(obj):
    """ checks if obj is book type"""
    return is_obj(obj) and obj.__obj_type__ == 'book'


def is_container(obj):
    """checks if obj is container type"""
    return is_obj(obj) and obj.__obj_type__ == 'container'


def can_contain_more(obj):
    """ checks to see if container can store more items """
    if not is_container(obj):
        return False

    obj_limit = int(obj.db.limit)

    # can hold infinite amount
    if obj_limit < 0:
        return True

    cur_item_count = len(obj.contents)
    if obj_limit < cur_item_count + 1:  # for the maybe extra added item
        return False
    return True


def can_pickup(ch, obj):
    """ tests whether obj can be picked up based on obj """
    if (obj.db.level > ch.attrs.level.value) or ("no_pickup" in obj.db.tags):
        return False

    # check to see if adding obj will overflow carry rating
    carry = ch.attrs.carry
    if carry.cur + obj.db.weight > carry.max:
        return False

    return True


def can_drop(ch, obj):
    if is_cursed(obj) or is_equipped(obj):
        return False
    return True


def is_equippable(obj):
    """
    tests whether obj can be equipped or not
    """
    # both these attributes are unique and is not set to None
    # on Equipment Objects
    return (is_equipment(obj) or is_light(obj)) and obj.db.equippable


def is_wieldable(obj):
    """ tests if obj is a weapon and wieldable"""
    return (is_weapon(obj) or is_staff(obj)) and obj.db.wieldable


def is_wielded(obj):
    if not (is_weapon(obj) or is_staff(obj)):
        return False
    return obj.db.is_wielded


def is_worn(obj):
    """ tests if object is currently set as worn """
    if not is_equippable(obj):
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
