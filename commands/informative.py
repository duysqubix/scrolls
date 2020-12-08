"""
holds informative type of commands
"""
from evennia.server.sessionhandler import SESSIONS
from evennia.contrib.rplanguage import obfuscate_language
from world.calendar import DAYS, DAYS_IN_WEEK, HOLIDAYS, MONTHS, START_ERA, START_YEAR
from world.paginator import BookEvMore
from evennia import EvForm, EvTable
from evennia.contrib import custom_gametime
from evennia.utils import evmore
from evennia.utils.utils import inherits_from
from commands.command import Command
from world.utils.utils import can_see_obj, capitalize_sentence, is_book, is_container, is_equipped, is_invis, is_npc, is_obj, is_pc, is_pc_npc, is_wielded, is_worn, match_name, parse_dot_notation, rplanguage_parse_string
from evennia.utils.ansi import raw as raw_ansi


class CmdWho(Command):
    """
    Show all online

    Usage:
        who
    """

    key = 'who'
    locks = "cmd:all()"

    def func(self):
        ch = self.caller

        who_msg = "\n|w|[r       Players Online       |n\n"
        table = self.styled_table("Level", "Name", border='incols')
        for ses in SESSIONS.get_sessions():
            if not ses.logged_in:
                continue
            vict = ses.get_account().puppet

            level = vict.attrs.level.value
            race = vict.attrs.race.name.capitalize()
            name = vict.name.capitalize()
            table.add_row(f"[{level:<3}{race:>10}]", name)
        ch.msg(who_msg + str(table))


class CmdTime(Command):
    """
    Displays the current date on Mundus

    Usage:
        time
    """

    key = 'time'
    locks = "cmd:all()"

    def func(self):
        ch = self.caller
        year, month, day, hour, min, sec = custom_gametime.custom_gametime(
            absolute=True)
        era = START_ERA
        epoch_year = START_YEAR

        while day > DAYS_IN_WEEK:
            day -= DAYS_IN_WEEK

        weekday = DAYS[day - 1]

        cur_month = MONTHS[month]

        if day == 1:
            suffix = 'st'
        elif day == 2:
            suffix = 'nd'
        elif day == 3:
            suffix = 'rd'
        else:
            suffix = 'th'

        time_of_day = "|cAM|Y" if hour < 12 else "|RPM|Y"
        if hour > 12:
            hour -= 12

        holiday = ""
        if day in HOLIDAYS[month].keys():
            holiday = HOLIDAYS[month][day]
            holiday = "|b*|g" + holiday + "|b*|Y"

        string = r"""
           |Y.-.---------------------------------.-.
          |y((|ro|y))      |w{day:>2}{suffix} |nof |c{cur_month:<15}|y      )|n
           |x\U/|Y_______          _____         ____/
            |Y |                                  |
             |         |W{weekday:>7}, {era}E{year:<3}|Y           |
             |          |W{hour:02}:{min:02}:{sec:02} {tod:<2}|Y             |
             |                                  |
             |____    _______    __  ____     ___|   
            |x/A\|Y                                  \
           |y((|ro|y))|Y     {holiday:<25}    
            '-'----------------------------------'|n
        """.format(era=era,
                   year=year + epoch_year,
                   weekday=weekday,
                   day=day,
                   suffix=suffix,
                   cur_month=cur_month,
                   hour=hour,
                   min=min,
                   sec=sec,
                   tod=time_of_day,
                   holiday=holiday)
        ch.msg(string)


class CmdAffect(Command):
    """
    Shows current affects on you

    Usage:
        affect
    """

    key = 'affect'
    aliases = ['af']
    locks = "cmd:all()"

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
        read <num>.book
    """

    key = 'read'
    locks = "cmd:all()"

    def func(self):
        ch = self.caller

        def show_book(book):
            title = book.db.title
            author = book.db.author
            contents = book.db.contents
            date = book.db.date

            book_contents = f"\n|gTitle|w: {title}\n|gAuthor|w: {author}\n|gDate|w: {date}\n\n|n"
            # evmore.msg(ch, book_contents)
            form = EvForm("resources.forms.book")
            form.map(cells={1: book.db.title, 2: book.db.author})

            # translate book into language as specified in book extra settings
            book_lang = book.db.language
            lang_skill = ch.languages.get(book_lang, None)
            if not lang_skill:  # language doesn't exist
                BookEvMore(ch, book_contents + contents)
            else:
                ch.debug_msg(book_lang, lang_skill)
                contents_translated = obfuscate_language(contents,
                                                         level=1.0 -
                                                         lang_skill.level,
                                                         language=book_lang)
                contents_translated = capitalize_sentence(contents_translated)
                BookEvMore(ch, book_contents + contents_translated)

        if not self.args:
            ch.msg("what do you want to read?")
            return

        obj_name = self.args.strip()
        pos, book = None, None
        if "." in obj_name:
            pos, book = obj_name.split('.')
            if book != 'book':
                ch.msg("if using dot expression, you must use book")
                return
            try:
                pos = int(pos)
            except:
                ch.msg("not a valid position number")
                return
        cntr = 1
        for obj in ch.contents:

            if is_book(obj):
                if obj_name in obj.db.name and not pos and not book:  # using object name instead of dot expression
                    show_book(obj)
                    return
                else:
                    # assume we are using dot expression
                    if cntr == pos:
                        show_book(obj)
                        return
                    cntr += 1
        ch.msg("You couldn't find anything to read")


class CmdEquipment(Command):
    """
    view currently worn equipment

    Usage:
        eq
        equipment
    """

    key = 'equipment'
    aliases = ['equip', 'eq']
    locks = "cmd:all()"

    def func(self):
        ch = self.caller
        wear_loc = ch.equipment._valid_wear_loc

        # # equipment
        table = self.styled_table(border=None)
        for loc in wear_loc:
            obj = ch.equipment.location[loc.name]
            if is_obj(obj):
                if not can_see_obj(ch, obj):
                    sdesc = "|C<something>|n"
                else:
                    sdesc = obj.obj_desc()
            else:
                sdesc = "|Mnothing|n"
            table.add_row(loc.display_msg, sdesc)

        msg = f"You are using\n{table}"
        ch.msg(msg)


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
        items = list(ch.contents)
        if not items:
            string = "You are not carrying anything."
        else:

            items.sort(key=lambda x: x.db.sdesc.lower())
            table = self.styled_table(border="header")
            for item in items:
                if is_worn(item) or is_wielded(item):
                    continue

                if not can_see_obj(ch, item):
                    sdesc = "<something>"
                else:
                    sdesc = f"{item.obj_desc()}"
                table.add_row("{}|n".format(raw_ansi(sdesc)))
            string = f"|wYou are carrying:\n{table}"
        ch.msg(string)


class CmdLook(Command):
    """
    Look at location of object

    Usage:
        look
        look <obj>
        look <pc||npc>
        look in <container>

    """

    key = "look"
    aliases = ['l', 'ls']
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        ch = self.caller
        location = ch.location
        if not self.args:
            if not self:
                ch.msg("You have no location to look at!")
                return

            room_msg = ""

            # get room title
            room_msg += f"|c{location.db.name}|n\n"

            #get room_desc
            room_msg += f"|G{location.db.desc}|n\n\n"

            # get room exits
            room_msg += "|C[ Exits: "
            for direction, dvnum in location.db.exits.items():
                if dvnum < 0:
                    continue  # not set

                room_msg += f"|lc{direction}|lt{direction}|le "
            room_msg += "]|n\n\n"

            # get room contents
            # get objects
            for obj in sorted(location.contents,
                              key=lambda x: x.db.look_index):
                if is_pc(obj):
                    if obj.id == ch.id:
                        continue
                    room_msg += f"{obj.name.capitalize()}\n"

                elif is_npc(obj) and can_see_obj(ch, obj):
                    room_msg += f"{obj.db.ldesc}\n"

                elif is_obj(obj):
                    if is_invis(obj) and not can_see_obj(ch, obj):
                        ch.msg("Couldn't see")
                        continue
                    else:
                        room_msg += f"{obj.obj_desc(ldesc=True)}\n"
            ch.msg(room_msg)
            return

        args = self.args.strip().split()
        # attempt to look at something specific in the room

        # try looking for obj in room based on name or aliases

        if len(args) == 1:
            obj_name = args[0]

            # attempt to look for edesc in room itself
            edesc = location.db.edesc
            if obj_name in edesc.keys():
                msg = f"\n\n{rplanguage_parse_string(ch, edesc[obj_name])}"
                evmore.EvMore(ch, msg)
                return
            # look for obj in room
            for obj in ch.location.contents:
                if is_obj(obj):
                    if obj_name in obj.db.name:
                        edesc = rplanguage_parse_string(ch, obj.db.edesc)
                        ch.msg(edesc)
                        return
                elif is_npc(obj):
                    if obj_name in obj.db.key:
                        edesc = rplanguage_parse_string(ch, obj.db.edesc)
                        ch.msg(edesc)
                        return
            # try looking for an obj in your inventory, if found send back edesc
            for obj in ch.contents:
                if is_equipped(obj):
                    continue
                if match_name(obj_name, obj):
                    edesc = obj.db.edesc
                    if not edesc:
                        ch.msg("You see nothing interesting.")
                    else:
                        edesc = rplanguage_parse_string(ch, edesc)
                        ch.msg(edesc)
                    return
            ch.msg("You don't see anything like that.")
            return

        if len(args) == 2:
            _filler, con_name = args
            if _filler != 'in':
                ch.msg("Supply `in` when looking in a container")
                return
            pos, con_name = parse_dot_notation(con_name)

            cntr = 1
            locs = [ch, ch.location]
            for loc in locs:
                for obj in loc.contents:
                    if not is_container(obj):
                        continue
                    if match_name(con_name, obj) and (cntr == pos or not pos):
                        # found container; display contents, sorted
                        objs = list(obj.contents)
                        objs.sort(key=lambda x: x.db.sdesc.lower())
                        table = self.styled_table(border="header")
                        for item in objs:
                            if not can_see_obj(ch, item):
                                sdesc = "<something>"
                            else:
                                sdesc = f"{item.obj_desc()}"
                            table.add_row("{}|n".format(raw_ansi(sdesc)))
                        extra = "" if not is_pc_npc(
                            loc) else ", that you are holding,"
                        string = f"|w{obj.db.sdesc}{extra} has:\n{table}"
                        ch.msg(string)
                        return
                    cntr += 1
            ch.msg("You couldn't find anything like that.")


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
            21: ch.attrs.gender.value.value.capitalize(),
            22: green_or_red(ch.attrs.AR.value),
            23: green_or_red(ch.attrs.MAR.value)
        })

        languages = [
            x.capitalize() for x in ch.languages.all()
            if (x != 'name') and (ch.languages.get(x).level > 0.0)
        ]
        lan_skill = [
            x.name.capitalize() for x in ch.languages.all(return_obj=True)
            if x.level > 0.0
        ]
        table = EvTable("Language",
                        "Rank",
                        table=[languages, lan_skill],
                        border='incols')
        form.map(tables={"A": table})
        ch.msg(form)
