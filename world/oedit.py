"""
Main EvMenu that handles editing objects
"""
import copy
from typeclasses.objs.custom import CUSTOM_OBJS
from evennia import GLOBAL_SCRIPTS
from evennia.utils.eveditor import EvEditor
from evennia import CmdSet
from evennia.utils.utils import dedent
from commands.command import Command
from evennia.commands.default.help import CmdHelp

_DEFAULT_OBJ_STRUCT = {
    'key': "an unfinshed object",
    'sdesc': "an unfinshed object",
    'ldesc': "an unfinished object is lying here",
    "adesc": None,  # action desciption, message string announced when used
    "type":
    'default',  # type of object: book, weapon, equipment, scroll, etc...
    "wear_flags": None,  #take, head, armor, wield, shield, etc..
    "weight": 0,
    "cost": 0,
    "level": 0,  # minimum level that can use this object
    "applies":
    [],  # temporarily changes stats, attrs, and conditions while using
    "extra": {}  # holds special fields relatd to a special object
}

_OEDIT_PROMPT = "(|goedit|n) > "


class OEditMode:
    _max_edit_len = 50

    def __init__(self, caller, vnum) -> None:
        self.caller = caller
        self.vnum = vnum
        self.db = GLOBAL_SCRIPTS.objdb
        self.obj = None
        self.prompt = _OEDIT_PROMPT

        # attempt to find vnum in objdb
        if self.vnum in self.db.vnum.keys():
            self.obj = self.db.vnum[self.vnum]

            # account for new fields added to default object builder
            for field, value in _DEFAULT_OBJ_STRUCT.items():
                if field not in self.obj.keys():
                    self.obj[field] = value

            # if obj is a special type based on type, add those
            # extra fields here
            obj_type = self.obj['type']
            extra_fields = CUSTOM_OBJS[obj_type].__obj_specific_fields__
            self.obj['extra'] = extra_fields

        else:
            self.caller.msg("creating new obj vnum: [{self.vnum}]")
            self.obj = copy.deepcopy(_DEFAULT_OBJ_STRUCT)

    def _cut_long_text(self, txt):
        txt = str(txt)
        max_len = self._max_edit_len
        if len(txt) < max_len:
            return txt
        else:
            return txt[:max_len] + "[...]"

    def save(self):
        self.db.vnum[self.vnum] = self.obj

    def summarize(self):
        # max_len = 50
        # if len(self.obj['ldesc']) < max_len:
        #     ldesc = self.obj['ldesc']
        # else:
        #     ldesc = self.obj['ldesc'][:max_len] + "[...]"
        ldesc = self._cut_long_text(self.obj['ldesc'])
        msg = f"""
********Summary*******

VNUM: [{self.vnum}]

key    : |y{self.obj['key']}|n
sdesc  : |y{self.obj['sdesc']}|n
ldesc  : 
|y{ldesc}|n

adesc  : {self.obj['adesc']}
type   : {self.obj['type']}
wear   : {self.obj['wear_flags']}
weight : {self.obj['weight']}
cost   : {self.obj['cost']}
level  : {self.obj['level']}
applies: {", ".join(self.obj['applies'])}
----------------Extras---------------------
"""
        self.caller.msg(self.obj['extra'])
        for efield, evalue in self.obj['extra'].items():
            msg += f"{efield:<7}: {evalue}\n"
        self.caller.msg(msg)


class OEditCmdSet(CmdSet):
    key = "OEditMode"

    mergetype = "Replace"

    def at_cmdset_creation(self):
        self.add(Exit())
        self.add(Look())
        self.add(CmdHelp())
        self.add(Set())


class OEditCommand(Command):
    def at_post_cmd(self):
        self.caller.msg(prompt=_OEDIT_PROMPT)


class Set(OEditCommand):
    """
    Sets various items on currently editting object.
    
    Usage:
        set key <comma seperated keywords>
        set sdesc [desc] <- ignoring desc will bring EvEditor
        set ldesc [desc] <- same as above
        set adesc [desc] <- same as above
        set type <- Enters EvMenu
        set wear <- Enters EvMenu
        set weight <weight in lbs>
        set cost <cost>
        set level <level>
        set applies <- enters EvMenu
    """
    key = 'set'

    # valid_obj_attributes = [
    #     'key', 'sdesc', 'ldesc', 'adesc', 'type', 'wear', 'weight', 'cost',
    #     'level', 'applies', 'extra'
    # ]
    valid_obj_attributes = list(_DEFAULT_OBJ_STRUCT.keys())

    def func(self):
        ch = self.caller
        args = self.args.strip().split()
        obj = ch.ndb._oedit.obj
        if not args:
            keywords = "|n\n*|c".join(self.valid_obj_attributes)
            ch.msg(
                f'you must provide one of the valid keywords.\n*|c{keywords}')
            return

        keyword = args[0].lower()
        if keyword not in self.valid_obj_attributes:
            ch.msg("that obj attribute doesn't exist.")
            return

        if keyword in ('key', 'sdesc', 'ldesc', 'adesc'):
            # keyword is key, sdesc, ldesc, adesc
            if len(args) > 1:
                # here the user set the value of the supplied keyword
                # directly in the field, set it and return
                obj[keyword] = " ".join(args[1:]).strip()
                ch.msg(f"{keyword} set.")
            else:
                # open eveditor
                def save_func(_caller, buffer):
                    obj[keyword] = buffer
                    ch.msg(f"{keyword} set.")

                _ = EvEditor(ch,
                             loadfunc=(lambda _x: obj[keyword]),
                             savefunc=save_func)

        elif keyword == 'type':
            if len(args) > 1:
                selected_type = args[1].strip()
                if selected_type not in CUSTOM_OBJS.keys():
                    ch.msg("that is not a valid obj type")
                    return

                # remove old fields
                cur_obj_type = CUSTOM_OBJS[obj['type']]
                field_to_rm = cur_obj_type.__obj_specific_fields__
                for field in field_to_rm:
                    del obj['extra'][field]

                obj[keyword] = selected_type
                # also reinit oeditmode to add new fields
                ch.ndb._oedit.__init__(ch, ch.ndb._oedit.vnum)
                ch.msg(f"object type changed `{selected_type}`")
            else:
                # caller provides no type, list available types
                types = [x for x in CUSTOM_OBJS.keys()]
                types_str = "\n".join(types)
                ch.msg(f"Available Types:\n{types_str}")
                return

        elif keyword == 'extra':
            # set extra fields this will be ambiguous depending
            # on custom object type
            if len(args) > 1:
                extra_keyword = args[1]
                if extra_keyword not in obj['extra'].keys():
                    ch.msg("not a valid extra keyword")
                    return

                if len(args) == 2:
                    # ex: set extra subkey
                    # open editor
                    def save_func(_caller, buffer):
                        obj[keyword][extra_keyword] = buffer
                        ch.msg(f"{extra_keyword} set.")

                    _ = EvEditor(ch,
                                 loadfunc=(lambda _x: obj[keyword]),
                                 savefunc=save_func)

                else:
                    # args is more than 3
                    obj[keyword][extra_keyword] = " ".join(args[2:]).strip()
                    ch.msg(f"{extra_keyword} set.")

            else:
                # list available extras that can be set
                msg = "Available Extra Fields:\n"
                for efield in obj['extra'].keys():
                    msg += f"{efield}\n"
                ch.msg(msg)


class Look(OEditCommand):
    """
    view currently editing objects main stats

    Usage:
        look
    """
    key = "look"
    aliases = ['l', 'ls']

    def func(self):
        ch = self.caller
        ch.ndb._oedit.summarize()


class Exit(OEditCommand):
    """
    Exit oedit.

    Usage:
        exit
    """
    key = "exit"

    def func(self):
        ch = self.caller
        ch.cmdset.remove('world.oedit.OEditCmdSet')
        ch.ndb._oedit.save()
        del ch.ndb._oedit
