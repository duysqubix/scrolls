"""
holds informative type of commands
"""
from evennia import EvForm
from evennia.utils import evmore, crop
from evennia.utils.utils import inherits_from
from commands.command import Command


class CmdAffect(Command):
    """
    Shows current affects on you

    Usage:
        affect
    """

    key = 'affect'
    aliases = ['af']

    def func(self):
        ch = self.caller

        conditions = ch.conditions.conditions
        traits = ch.traits.traits
        ch.msg("You are affected by the following:\n")
        msg = "Conditions:\n"
        # conditions
        for con in conditions:
            msg += f"|g{str(con).replace('_', ' ').capitalize()}|n\n"

        # traits
        msg += "\nTraits:\n"
        for trait in traits:
            msg += f"|g{str(trait).replace('_', ' ').capitalize()}|n\n"

        ch.msg(msg)
        #spells


class CmdRead(Command):
    """
    Books are enjoyable to read no matter
    who or where you hail from. Grab a book,
    pick a spot, and let it take you away on
    an adventure.

    Usage:
        read <bookname>
    """

    key = 'read'

    def func(self):
        ch = self.caller
        if not self.args:
            ch.msg("what do you want to read?")
            return

        obj_name = self.args.strip()

        for obj in ch.contents:
            if inherits_from(
                    obj, 'typeclasses.objs.custom.Book') and (obj_name
                                                              in obj.db.name):
                title = obj.db.title
                author = obj.db.author
                contents = obj.db.contents

                book_contents = f"Title: {title}\nAuthor: {author}\n\n{contents}"
                evmore.msg(ch, book_contents)
                return
        ch.msg("You couldn't find anything to read")


class CmdInventory(Command):
    """
    view inventory
    Usage:
      inventory
      inv
    Shows your inventory.
    """

    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"
    arg_regex = r"$"

    def func(self):
        """check inventory"""
        ch = self.caller
        items = ch.contents
        if not items:
            string = "You are not carrying anything."
        else:
            from evennia.utils.ansi import raw as raw_ansi

            table = self.styled_table(border="header")
            for item in items:
                table.add_row(
                    "{}|n".format(
                        crop(raw_ansi(item.db.sdesc), width=50) or ""), )
            string = f"|wYou are carrying:\n{table}"
        ch.msg(string)


class CmdLook(Command):
    """
    Look at location of object

    Usage:
        look
        look <obj>
        look <character>
    """

    key = "look"
    aliases = ['l', 'ls']
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        ch = self.caller
        # if not self.args:
        #     target = ch.location
        #     if not target:
        #         ch.msg("You have no location to look at!")
        #         return
        # else:
        #     target = ch.search(self.args)
        #     if not target:
        #         ch.msg("You don't see anything like that")
        #         return

        # room
        if not self.args:
            target = ch.location
            if not target:
                ch.msg("You have no location to look at!")
                return

            room_msg = ""

            # get room title
            room_msg += f"|c{target.name}|n\n"

            #get room_desc
            room_msg += f"|G{target.db.desc}|n\n\n"

            # get room exits

            # get room contents
            # get objects
            for obj in target.contents:
                if inherits_from(obj, 'typeclasses.characters.Character'):
                    if obj.id == ch.id:
                        continue
                    room_msg += f"{obj.name.capitalize()}\n"
                if obj.db.sdesc:
                    room_msg += f"{obj.db.ldesc}\n"
            ch.msg(room_msg)
            return

        # try looking for obj in room based on name or aliases
        obj_name = self.args.strip()
        for obj in ch.location.contents:
            if obj.db.name:
                if obj_name in obj.db.name:
                    ch.msg(obj.db.edesc)
                    return
        ch.msg("You don't see anything like that.")

        # self.msg((ch.at_look(target), {"type": "look"}), options=None)


class CmdScore(Command):
    """
    show information about yourself

    Usage:
        score
    """

    key = 'score'
    locks = "cmd:all()"

    def func(self):
        ch = self.caller

        def green_or_red(num):
            if num < 0:
                return f"|r{num}|n"
            elif num > 0:
                return f"|g{num}|n"
            else:
                return f"{num}"

        #TODO change path to EvForm to  use
        form = EvForm("resources.score_form")
        form.map({
            1: ch.name.capitalize(),
            2: ch.stats.str.base,
            3: green_or_red(ch.stats.str.bonus),
            4: ch.stats.agi.base,
            5: green_or_red(ch.stats.agi.bonus),
            6: ch.stats.end.base,
            7: green_or_red(ch.stats.end.bonus),
            8: ch.stats.wp.base,
            9: green_or_red(ch.stats.wp.bonus),
            10: ch.attrs.level.value,
            11: ch.stats.lck.base,
            12: green_or_red(ch.stats.lck.bonus),
            13: ch.stats.int.base,
            14: green_or_red(ch.stats.int.bonus),
            15: ch.stats.prs.base,
            16: green_or_red(ch.stats.prs.bonus),
            17: ch.stats.prc.base,
            18: green_or_red(ch.stats.prc.bonus),
            19: str(ch.attrs.birthsign.value),
            20: ch.attrs.race.value.name.capitalize(),
            21: ch.attrs.gender.value.value.capitalize()
        })
        ch.msg(form)
