"""
on-line editing of objects
"""
from typeclasses.objs.object import VALID_OBJ_APPLIES, VALID_OBJ_TAGS
from evennia.utils.utils import inherits_from
from typeclasses.objs.custom import CUSTOM_OBJS
from evennia import GLOBAL_SCRIPTS
from evennia import CmdSet, EvEditor, EvMenu
from commands.command import Command
from evennia.commands.default.help import CmdHelp
from .model import _EditMode

from world.globals import DEFAULT_OBJ_STRUCT
_OEDIT_PROMPT = "(|goedit|n) > "


class OEditMode(_EditMode):
    __cname__ = "obj"
    __db__ = GLOBAL_SCRIPTS.objdb
    __prompt__ = _OEDIT_PROMPT
    __default_struct__ = DEFAULT_OBJ_STRUCT
    _max_edit_len = 50

    @property
    def custom_objs(self):
        return CUSTOM_OBJS

    def _cut_long_text(self, txt):
        txt = str(txt)
        max_len = self._max_edit_len
        if len(txt) < max_len:
            return txt
        else:
            return txt[:max_len] + "[...]"

    def save(self, override=False, bypass_checks=False):
        if (self.orig_obj != self.obj) or override:

            if not bypass_checks:
                # custom object checks here
                if self.obj['type'] == 'equipment':
                    wear_loc = self.obj['extra']['wear_loc']
                    wear_loc = wear_loc.split(' ')
                    self.obj['extra']['wear_loc'] = wear_loc[0]
                    try:
                        self.obj['extra']['AR'] = int(self.obj['extra']['AR'])
                        self.obj['extra']['MAR'] = int(
                            self.obj['extra']['MAR'])
                    except ValueError:
                        self.caller.msg(
                            "AR/MAR of equipment is not valid integers")
                        return

                # if self.obj['type'] == 'weapon':
                #     dual_wield = self.obj['extra']['dual_wield']
                #     self.obj['extra']['dual_wield'] = bool(dual_wield)

                if self.obj['type'] == 'container':
                    limit = self.obj['extra']['limit']
                    self.obj['extra']['limit'] = int(limit)

            self.db.vnum[self.vnum] = self.obj
            self.caller.msg("object saved.")

    def summarize(self):
        def applies_to_pretty(x):
            self.caller.msg(x)
            msg = ""
            split = 3
            cntr = 0
            for c in x:
                if cntr == split:
                    msg += "\n"
                    cntr = 0
                msg += f"|g{c[0]}|n"
                for i in c[1:]:
                    if i is None:
                        break
                    else:
                        msg += f"[{i}]"
                msg += ", "
                cntr += 1
            return msg

        applies = applies_to_pretty(self.obj['applies'])
        msg = f"""
********Obj Summary*******

|GVNUM|n: [{self.vnum}]

|Gkey|n    : {self.obj['key']}
|Gsdesc|n  : {self.obj['sdesc']}
|Gldesc|n  : 
{self._cut_long_text(self.obj['ldesc'])}

|Gedesc|n  : {self._cut_long_text(self.obj['edesc'])}
|Gadesc|n  : {self.obj['adesc']}
|Gtype|n   : {self.obj['type']}
|Gweight|n : {self.obj['weight']}
|Gcost|n   : {self.obj['cost']}
|Glevel|n  : {self.obj['level']}
|Gapplies|n: 

{applies}

|Gtags|n   : {", ".join(self.obj['tags'])}
----------------Extras---------------------
"""
        self.caller.msg(self.obj['extra'])
        for efield, evalue in self.obj['extra'].items():
            msg += f"{efield:<7}: {self._cut_long_text(evalue)}\n"
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

    valid_obj_attributes = list(DEFAULT_OBJ_STRUCT.keys())

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

        if keyword in ('key', 'sdesc', 'edesc', 'ldesc', 'adesc'):
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
                field_to_rm = cur_obj_type.__specific_fields__
                for field in field_to_rm:
                    del obj['extra'][field]

                obj[keyword] = selected_type
                ch.ndb._oedit.save(
                    override=True, bypass_checks=True
                )  # force save, so it can update apporpriately
                # also reinit oeditmode to add new fields
                ch.ndb._oedit.__init__(ch, ch.ndb._oedit.vnum)
                ch.msg(f"object type changed `{selected_type}`")
            else:
                # caller provides no type, list available types
                types = [x for x in CUSTOM_OBJS.keys()]
                types_str = "\n".join(types)
                ch.msg(f"Available Types:\n{types_str}")
                return
        elif keyword in ('weight', 'cost', 'level'):
            # set can't be < 0
            try:
                weight = int(args[1].strip())
            except:
                ch.msg(f"{keyword} not a valid integer")
                return

            if weight < 0:
                weight = 0
            obj[keyword] = weight
            ch.msg(f'{keyword} set.')
            return

        elif keyword == 'applies':
            #args=    [0]     [1]    [2]    [3]  [4]
            # ex: set applies attrs [attr] [mod]
            # ex: set applies stats [stat] [mod]
            # ex: set applies conditions blinded x,y
            if len(args) > 1:
                if args[1] == 'clear':
                    obj[keyword].clear()
                    return
                if len(args) < 3:
                    ch.msg("invalid entry, see |chelp oedit-menu-applies|n")
                    return

                apply_type = args[1]
                if apply_type not in VALID_OBJ_APPLIES.keys():
                    ch.msg("not a valid apply type")
                    return

                if apply_type == 'attrs':
                    attr = args[2]
                    if attr not in VALID_OBJ_APPLIES['attrs']:
                        ch.msg("not a valid attribute to modify")
                        return
                    try:
                        mod = int(args[3])
                    except:
                        ch.msg("not a valid number for modifier")
                        return

                    pair = (attr, mod)
                    if pair in obj[keyword]:
                        obj[keyword].remove(pair)
                        return
                    obj[keyword].append(pair)

                elif apply_type == 'stats':
                    stat = args[2]
                    if stat not in VALID_OBJ_APPLIES['stats']:
                        ch.msg("not a valid stat to modify")
                        return
                    try:
                        mod = int(args[3])
                    except:
                        ch.msg("not a valid number for modifier")
                        return

                    pair = (stat, mod)
                    if pair in obj[keyword]:
                        obj[keyword].remove(pair)
                        return
                    obj[keyword].append(pair)

                elif apply_type == 'conditions':
                    # ex: set applies conditions <condition> x y
                    condition = args[2]
                    if condition not in VALID_OBJ_APPLIES['conditions']:
                        ch.msg("not a valid condition")
                        return

                    x, y = None, None
                    if len(args) == 4:
                        # only x is given
                        try:
                            #TODO: sometimes x can be float depending on condition
                            x = int(args[3])
                        except:
                            ch.msg("X must be valid number")
                            return
                    elif len(args) == 5:
                        # x and y is given
                        try:
                            x = int(args[3])
                            y = int(args[4])
                        except:
                            ch.msg("XY must be a valid number")
                            return

                    pair = (condition, x, y)
                    if pair in obj[keyword]:
                        obj[keyword].remove(pair)
                        return
                    obj[keyword].append(pair)
                else:
                    raise ValueError(
                        "bug encountered, you shouldn't have gotten here.")
            else:
                # show all applies
                applies = ""
                for apply_type, components in VALID_OBJ_APPLIES.items():
                    applies += f"\n|c{apply_type}|n\n    "
                    c = ", ".join(components)
                    applies += c

                ch.msg(applies)
                return

        elif keyword == 'tags':
            if len(args) > 1:
                tag = args[1].strip()

                if tag == 'clear':
                    obj[keyword].clear()
                    return
                if tag not in VALID_OBJ_TAGS:
                    ch.msg("Not a valid tag")
                    return
                if tag in obj[keyword]:
                    obj[keyword].remove(tag)
                    ch.msg(f"{tag} tag removed")
                else:
                    obj[keyword].append(tag)
                    ch.msg(f"{tag} tag applied")
                return
            else:
                # show all tags
                tags = ", ".join(VALID_OBJ_TAGS)
                msg = f"Available Tags:\n{tags}"
                ch.msg(msg)
                return
        #TODO: set safeguards if extra fields are set that aren't
        # part of the individual objects specific field rules
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

                    _ = EvEditor(
                        ch,
                        loadfunc=(lambda _x: obj[keyword][extra_keyword]),
                        savefunc=save_func)

                else:
                    # args is more than 3
                    obj[keyword][extra_keyword] = " ".join(args[2:]).strip()
                    ch.msg(f"{extra_keyword} set.")

            else:
                # list available extras that can be set
                msg = "Available Extra Fields:\n    "
                msg += "\n    ".join(CUSTOM_OBJS[obj['type']].__help_msg__)

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
        ch.cmdset.remove('world.edit.oedit.OEditCmdSet')
        try:
            b = bool(eval(self.args.strip().capitalize()))
            ch.ndb._oedit.save(override=b)
            del ch.ndb._oedit
        except:
            ch.ndb._oedit.save(override=False)
            del ch.ndb._oedit