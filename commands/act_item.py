from evennia.utils.utils import make_iter, uses_database
from commands.command import Command
from world.utils.act import Announce, act
from world.utils.utils import can_drop, can_see_obj, is_container, is_cursed, is_equippable, is_equipped, is_obj, can_pickup, is_sleeping, is_weapon, is_wieldable, is_wielded, is_worn, match_name, parse_dot_notation


class CmdPut(Command):
    """
    Put an object from your inventory into a valid container object

    Usage:
        put all in <container>
        put <obj> in <container>                
        put <obj> in <pos>.<container>          
        put <pos>.<obj> in <pos>.<container>    
        put all.<obj> in <pos>.container     

    Examples:
        put book in bag

    """

    key = 'put'
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        ch = self.caller

        def success_put(obj, con_obj):
            act("$n puts $p in $P", True, True, ch, obj, con_obj,
                Announce.ToRoom)
            act("You put $p in $P", True, True, ch, obj, con_obj,
                Announce.ToChar)

        def find_container(con_name, pos=None):
            locs = [ch, ch.location]
            for loc in locs:
                if pos is None:
                    # find first container
                    _container = None
                    for obj in loc.contents:
                        if is_container(obj) and match_name(con_name, obj):
                            # match
                            _container = obj
                            return _container
                else:
                    try:
                        pos = int(pos)
                    except:
                        raise ValueError('pos should be a integer value')

                    # find <pos> container
                    cntr = 1
                    _container = None
                    for obj in loc.contents:
                        if is_container(obj) and match_name(con_name, obj):
                            if cntr == con_pos:
                                # match container
                                _container = obj
                                return _container
                            cntr += 1

        def find_obj(obj_name, pos=None):
            # get all objects
            if pos is None and obj_name == 'all':
                # simple return all contents that isn't container type
                matched_objs = []

                for obj in ch.contents:
                    if is_container(obj) or is_equipped(obj):
                        continue
                    matched_objs.append(obj)
                return matched_objs

            # put book in bag
            elif pos is None:
                for obj in ch.contents:
                    if not is_container(obj) and match_name(
                            obj_name, obj) and not is_equipped(obj):
                        return make_iter(obj)
                return None

            # put all.book in bag
            elif pos == 'all':
                matched_objs = []
                for obj in ch.contents:
                    if not is_container(obj) and match_name(
                            obj_name, obj) and not is_equipped(obj):
                        matched_objs.append(obj)
                return matched_objs

            else:
                # get <pos> of matching name
                cntr = 1
                for obj in ch.contents:
                    if not is_container(obj) and match_name(
                            obj_name, obj) and not is_equipped(obj):
                        if cntr == pos:
                            return make_iter(obj)
                        cntr += 1
                return None

        args = self.args.strip().split()
        if not args or len(args) != 3:
            ch.msg("Put what in what?")
            return

        obj_name, _filler, container = args
        if _filler != 'in':
            ch.msg("You must speicify `in`")
            return

        all_objs = False
        obj_pos = con_pos = None

        obj_pos, obj_name = parse_dot_notation(obj_name)
        if obj_pos == 'all':
            all_objs = True

        con_pos, container = parse_dot_notation(container)

        if not obj_pos and not con_pos:
            _container = find_container(container)
            objs = find_obj(obj_name)
            if not _container:
                ch.msg("You couldn't find such container")
                return
            if not objs:
                ch.msg("You couldn't find such item")
                return

            for obj in objs:
                if not can_see_obj(ch,
                                   obj) or is_equipped(obj) or is_cursed(obj):
                    ch.msg("You can't do that.")
                    continue

                obj.move_to(_container)
                success_put(obj, _container)

            return

        # obj=all.<obj>
        _container = find_container(container, pos=con_pos)
        if not _container:
            ch.msg("You could't find that container.")
            return

        pos = 'all' if all_objs else obj_pos

        objs = find_obj(obj_name, pos=pos)
        if not objs:
            ch.msg("You can't find anything like that.")
            return

        for obj in objs:
            if not can_see_obj(ch, obj) or is_cursed(obj):
                ch.msg("You can't do that.")
                continue

            obj.move_to(_container)
            success_put(obj, _container)
        return


class CmdGet(Command):
    """
    get an object from room or a valid container

    Usage:
      get|take book
      get|take 2.book
      get|take book from bag
      get|take all.book from all.bag
      get|take book from 2.bag
      get|take 1.book from all.bag
      get|take all.book from 1.bag

    """

    key = "get"
    aliases = ['take']
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """implements the command."""

        ch = self.caller

        def success_get(obj, con=None):
            if not con:
                act(f"$n picks up a $p.", True, True, ch, obj, None,
                    Announce.ToRoom)
                act(f"You pick up a $p", False, False, ch, obj, None,
                    Announce.ToChar)
            else:
                act(f"$n gets $p from $P", True, True, ch, obj, con,
                    Announce.ToRoom)
                act(f"You get $p from $P", False, False, ch, obj, con,
                    Announce.ToChar)

        if not self.args:
            ch.msg("Get what?")
            return

        args = self.args.strip().split()

        # example of get
        # get all
        # get book
        # get all.book
        # get 1.book from 1.bag
        # get all.book from all.bag
        # get all from chest

        # TODO: refactor this function

        # arg length == get in room
        if len(args) == 1:  #ex: get all.book, get 1.book, get book
            obj_pos, obj_name = parse_dot_notation(args[0])

            #ex: get all
            if obj_name == 'all':
                for obj in ch.location_contents():
                    if can_pickup(ch, obj):
                        obj.move_to(ch, quiet=True)
                        success_get(obj)
                return

            #ex: get all.book, 1.book
            cntr = 1
            got_something = False
            for obj in ch.location_contents():
                if can_pickup(ch, obj):
                    # all.book
                    if obj_pos == 'all' and match_name(obj_name, obj):
                        obj.move_to(ch, quiet=True)
                        success_get(obj)
                        got_something = True
                    # 1.book
                    if match_name(obj_name, obj):
                        if obj_pos == cntr or not obj_pos:
                            obj.move_to(ch, quiet=True)
                            success_get(obj)
                            return
                        cntr += 1
            if not got_something:
                ch.msg("You can't get that.")
            return

        # arg length == getting from a container either on self or in room
        # get 1.book from 1.bag
        # get book from chest  - in room
        elif len(args) == 3:
            obj_name, _filler, con_name = args
            if "from" != _filler:
                ch.msg("must supply `in` when getting from a container")
                return
            obj_pos, obj_name = parse_dot_notation(obj_name)
            con_pos, con_name = parse_dot_notation(con_name)

            locs = [ch.contents, ch.location.contents]

            ####### first find container(s) ################
            matched_containers = []
            for loc in locs:
                cntr = 1
                for obj in loc:
                    if is_container(obj):
                        # all.bag
                        if con_pos == 'all' and match_name(con_name, obj):
                            matched_containers.append(obj)
                        # 2.bag or bag <= first find
                        if match_name(con_name, obj):
                            if con_pos == cntr or not con_pos:
                                matched_containers.append(obj)

            if not matched_containers:
                ch.msg("Could not find that container.")
                return
            #################################################

            ###### find items from container ################
            found_something = False
            for con in matched_containers:
                cntr = 1
                for obj in con.contents:
                    if is_obj(obj):
                        # all.book
                        if obj_pos == 'all' and match_name(
                                obj_name, obj) or obj_name == 'all':
                            obj.move_to(ch, quiet=True)
                            success_get(obj, con)
                            found_something = True
                        elif match_name(obj_name, obj):
                            if obj_pos == cntr or not obj_pos:
                                obj.move_to(ch, quiet=True)
                                success_get(obj, con)
                                return
            if not found_something:
                ch.msg("Could not find that item.")
            return
            ##################################################

            ch.msg(
                str((matched_containers,
                     [x.location for x in matched_containers])))

            # get all

            # # attempt to find one item
            # obj_name = args[0]
            # if "." in obj_name:
            #     amt, obj_name = obj_name.split('.')
            #     if amt == 'all':
            #         matched_objs = []
            #         for obj in ch.location.contents:
            #             if is_obj(obj) and can_see_obj(ch, obj):
            #                 if match_name(obj_name, obj):
            #                     matched_objs.append(obj)
            #         if not matched_objs:
            #             ch.msg(f"You couldn't find anything like {obj_name}")
            #             return
            #         for obj in matched_objs:
            #             if can_pickup(ch, obj):
            #                 obj.move_to(ch)
            #                 act(f"$n picks up a $p.", True, True, ch, obj,
            #                     None, Announce.ToRoom)
            #                 act(f"You pick up a $p", False, False, ch, obj,
            #                     None, Announce.ToChar)
            #             else:
            #                 act("You can't pick up $p", False, False, ch, None,
            #                     None, Announce.ToChar)
            #         return
            #     else:
            #         try:
            #             amt = int(amt)
            #         except ValueError:
            #             ch.msg("specify integer when using order")
            #             return
            #         cntr = 0
            #         for obj in ch.location.contents:
            #             if is_obj(obj) and can_see_obj(ch, obj):
            #                 if match_name(obj_name, obj):
            #                     cntr += 1
            #                     if amt == cntr:
            #                         if can_pickup(ch, obj):
            #                             #this is the one
            #                             obj.move_to(ch)
            #                             act(f"$n picks up $p.", True, True, ch,
            #                                 obj, None, Announce.ToRoom)
            #                             act(f"You pick up $p", False, False,
            #                                 ch, obj, None, Announce.ToChar)
            #                             return
            #                         else:
            #                             act("You can't pick up $p", False,
            #                                 False, ch, None, None,
            #                                 Announce.ToChar)
            #                             return
            #         if cntr < amt:
            #             ch.msg("There aren't that many around")
            #             return
            #         if cntr == amt:
            #             ch.msg(
            #                 "obj should have returned before getting to this.. contact admin"
            #             )
            #             return
            #         if amt < 0:
            #             ch.msg("indexing with negatives? I don't think so..")
            #             return
            #         if cntr > amt:
            #             ch.msg("this seriously would even make sense...")
            #             return
            # elif obj_name == 'all':
            #     for obj in ch.location.contents:
            #         if is_obj(obj) and can_see_obj(ch, obj):
            #             if can_pickup(ch, obj):
            #                 obj.move_to(ch, quiet=True)
            #                 act(f"$n picks up a $p.", True, True, ch, obj,
            #                     None, Announce.ToRoom)
            #                 act(f"You pick up a $p", False, False, ch, obj,
            #                     None, Announce.ToChar)
            #             else:
            #                 act("You can't pick up $p", False, False, ch, None,
            #                     None, Announce.ToChar)
            # else:
            #     # do a find in room, return first match
            #     for obj in ch.location.contents:
            #         if is_obj(obj):
            #             if match_name(obj_name, obj):
            #                 if can_pickup(ch, obj):
            #                     # move obj to player inv
            #                     obj.move_to(ch)
            #                     act(f"$n picks up a $p.", True, True, ch, obj,
            #                         None, Announce.ToRoom)
            #                     act(f"You pick up a $p", False, False, ch, obj,
            #                         None, Announce.ToChar)
            #                     return
            #                 else:
            #                     act("You can't pick up $p", False, False, ch,
            #                         None, None, Announce.ToChar)


class CmdRemove(Command):
    """
    Remove a weapon or armor from your equipped equipment

    Usage:
        remove <obj>
        remove all
    """

    key = 'remove'
    locks = 'cmd:all()'

    def func(self):
        ch = self.caller
        if not self.args:
            ch.msg("What do you want to remove?")
            return

        obj_name = self.args.strip()

        success_remove = False
        for obj in ch.contents:
            if is_equippable(obj) and is_worn(obj) and not is_cursed(obj):
                # equipment
                if obj_name == 'all':
                    ch.equipment.remove(obj)
                    success_remove = True
                elif match_name(obj_name, obj):
                    ch.equipment.remove(obj)
                    return

            elif is_wieldable(obj) and is_wielded(obj) and not is_cursed(obj):
                # weapon
                if obj_name == 'all':
                    ch.equipment.unwield(obj)
                    success_remove = True

                elif match_name(obj_name, obj):
                    ch.equipment.unwield(obj)
                    return

        if not success_remove:
            ch.msg("You can't remove that")


class CmdDrop(Command):
    """
    drop something
    Usage:
      drop <obj>
      drop <amt>.<obj> #TODO
      drop all
    """

    key = "drop"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        """Implement command"""

        ch = self.caller
        args = self.args.strip()

        if not self.args:
            ch.msg("Drop what?")
            return

        def success_drop(obj):
            act("$n drops $p", True, True, ch, obj, None, Announce.ToRoom)
            act("You drop $p", True, True, ch, obj, None, Announce.ToChar)

        if "." in args:
            pos, obj_name = args.split('.')
            do_all = False
            if pos == 'all':
                do_all = True
            else:
                try:
                    pos = int(pos)
                except:
                    ch.msg("pos must be a valid integer")
                    return

            # handles dot notation
            cntr = 1
            for obj in ch.contents:
                if is_equipped(obj):
                    continue
                if match_name(obj_name, obj):
                    if do_all:
                        # match
                        if can_drop(ch, obj):
                            obj.move_to(ch.location, quiet=True)
                            success_drop(obj)
                        else:
                            ch.msg("You can't drop that.")
                        continue

                    if cntr == pos:
                        # match
                        if can_drop(ch, obj):
                            obj.move_to(ch.location, quiet=True)
                            success_drop(obj)
                        else:
                            ch.msg("You can't drop that.")

                    cntr += 1

        else:
            for obj in ch.contents:
                if is_equipped(obj):
                    continue

                if args == 'all':
                    if can_drop(ch, obj):
                        obj.move_to(ch.location, quiet=True)
                        success_drop(obj)

                    else:
                        act("You can't drop $p", False, False, ch, obj, None,
                            Announce.ToChar)
                    continue

                elif match_name(args, obj):
                    if can_drop(ch, obj):
                        obj.move_to(ch.location, quiet=True)
                        success_drop(obj)
                        return
                    else:
                        act("You can't drop $p", False, False, ch, obj, None,
                            Announce.ToChar)
                        return


class CmdWield(Command):
    """
    wield a weapon

    Usage:
        wield <obj>
    """
    key = 'wield'
    locks = 'cmd:all()'

    def func(self):
        ch = self.caller

        if not self.args:
            ch.msg("What do you want to wield?")
            return

        args = self.args.strip()
        for obj in ch.contents:
            if is_weapon(obj) and not is_wielded(obj):
                # potential candidate
                if match_name(args, obj):
                    # match
                    ch.equipment.wield(obj)
                    return

        ch.msg("You couldn't find anything like that to wield.")


class CmdWear(Command):
    """
    Dawn a piece of armor onto you from
    your inventory

    Usage:
        wear <obj>
        wear all
    """

    key = 'wear'
    locks = 'cmd:all()'

    def func(self):
        ch = self.caller

        if not self.args:
            ch.msg("What do you want to wear?")
            return

        args = self.args.strip()
        if args == 'all':
            for obj in ch.contents:
                if is_equippable(
                        obj) and not is_worn(obj) and not is_weapon(obj):
                    ch.equipment.add(obj)
            return
        for obj in ch.contents:
            if is_equippable(obj) and not is_worn(obj) and not is_weapon(obj):
                # this object is a potential candidate
                if match_name(args, obj):
                    # we have a match!
                    ch.equipment.add(obj)
                    return
        ch.msg("You couldn't find anything like that to wear")