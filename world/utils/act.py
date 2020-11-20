from enum import Enum
from world.utils.utils import can_see_obj, is_hidden, is_invis, is_pc, is_sleeping
from world.conditions import Sleeping
from world.gender import is_female, is_male, is_nogender


class Announce(Enum):
    ToRoom = 1
    ToVict = 2
    ToNotVict = 3
    ToChar = 4


def act(msg, hide_invisible, hide_sleep, ch, obj, vict_obj, announce_type):
    """
    A python conversion for ROM based act function.
    A specified string that is formatted based on passed arguments.

    Args:
        msg: formatted message
        hide_invisible: if True, it will hide output from objects that cannot see ch
        hide_sleep: if True, it will hide output from objects that are affected by Sleep
        ch: caller that invoked this function
        obj: an object that is not a room/pc/npc
        vict_obj: a targeted npc/pc 
        announce_type: type of announcement this act will generate
    
    Valid Token Definitions:
        $n - write name,short description, or 'someone' for ch depending on whether ch is a PC, NPC, or an invisible NPC/PC
        $N - like $n but for vict_obj
        $m - him, her, or it depending on gender of ch
        $M - like $m but for vict_obj
        $s - his, her, or it depending on gender of ch
        $S - like $s but for vict_obj
        $e - he, she, or it depending on gender of ch
        $E - like $e but for vict_objt
        $p - short description or 'something' for obj. 
        $P Like $p for vict_obj.*


        TODO Tokens:
        $o Name or 'something' for obj, depending on visibility. 
        $O Like $o, for vict_obj.*
        $a 'an' or 'a', depending on the first character of obj's name. 
        $A Like $a, for vict_obj.* 
        $$ Print the character '$' 
    Ex:
        act("$n yells frantically to whole room", FALSE, ch, None, None, Announce.ToRoom)
        act("$n tells $N to calm down", FALSE, ch, None, other_player, Announce.ToRoom)
        act("$n tells you to keep your voice down...", FALSE, ch, None, other_player, Announce.ToVict)
    """

    if "$n" in msg:
        if is_hidden(ch) or is_invis(ch):
            msg = msg.replace("$n", "someone")
        else:
            msg = msg.replace("$n", ch.name.capitalize())

    if "$N" in msg:
        if is_hidden(vict_obj) or is_invis(vict_obj):
            msg = msg.replace("$N", "someone")
        else:
            msg = msg.replace("$N", vict_obj.name.capitalize())
    if "$m" in msg:
        if is_hidden(ch) or is_invis(ch):
            msg = msg.replace("$m", 'someone')
        else:
            if is_male(ch):
                msg = msg.replace("$m", 'him')
            elif is_female(ch):
                msg = msg.replace('$m', 'her')
            else:
                msg = msg.replace('$m', 'it')

    if "$M" in msg:
        if is_hidden(vict_obj) or is_invis(ch):
            msg = msg.replace("$M", 'someone')
        else:
            if is_male(vict_obj):
                msg = msg.replace("$M", 'him')
            elif is_female(vict_obj):
                msg = msg.replace('$M', 'her')
            else:
                msg = msg.replace('$mM', 'it')

    if "$s" in msg:
        if is_hidden(ch) or is_invis(ch):
            msg = msg.replace("$s", 'someone')
        else:
            if is_male(ch):
                msg = msg.replace("$s", 'his')
            elif is_female(ch):
                msg = msg.replace('$s', 'her')
            else:
                msg = msg.replace('$s', 'it')

    if "$S" in msg:
        if is_hidden(vict_obj) or is_invis(ch):
            msg = msg.replace("$S", 'someone')
        else:
            if is_male(vict_obj):
                msg = msg.replace("$S", 'his')
            elif is_female(vict_obj):
                msg = msg.replace('$S', 'her')
            else:
                msg = msg.replace('$S', 'it')

    if "$e" in msg:
        if is_hidden(ch) or is_invis(ch):
            msg = msg.replace("$e", 'someone')
        else:
            if is_male(ch):
                msg = msg.replace("$e", 'he')
            elif is_female(ch):
                msg = msg.replace('$e', 'she')
            else:
                msg = msg.replace('$e', 'it')

    if "$E" in msg:
        if is_hidden(ch) or is_invis(ch):
            msg = msg.replace("$E", 'someone')
        else:
            if is_male(vict_obj):
                msg = msg.replace("$E", 'he')
            elif is_female(vict_obj):
                msg = msg.replace('$E', 'she')
            else:
                msg = msg.replace('$E', 'it')

    if "$p" in msg:
        #TODO: had invis and basic effects to objects

        sdesc = obj.db.sdesc
        msg = msg.replace('$p', sdesc)

    if "$P" in msg:
        sdesc = vict_obj.db.sdesc
        msg = msg.replace("$P", sdesc)

    if announce_type == Announce.ToRoom:
        for obj in ch.location.contents:
            if is_pc(obj):
                if (hide_invisible and is_invis(obj)) or (
                        hide_sleep and is_sleeping(obj)) or (obj.id == ch.id):
                    continue
                obj.msg(msg)
        return
    if announce_type == Announce.ToChar:
        ch.msg(msg)
        return
    if announce_type == Announce.ToVict:
        if is_pc(vict_obj):
            if is_sleeping(vict_obj) and hide_sleep:
                return

            vict_obj.msg(msg)
        return
    if announce_type == Announce.ToNotVict:
        ch.location.announce(msg, exclude=[vict_obj])
        return
