from enum import Enum
from world.conditions import Sleeping


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

        TODO Tokens:
        $o Name or 'something' for obj, depending on visibility. 
        $O Like $o, for vict_obj.*
        $p Short description or 'something' for obj. 
        $P Like $p for vict_obj.*
        $a 'an' or 'a', depending on the first character of obj's name. 
        $A Like $a, for vict_obj.* 
        $$ Print the character '$' 
    Ex:
        act("$n yells frantically to whole room", FALSE, ch, None, None, Announce.ToRoom)
        act("$n tells $N to calm down", FALSE, ch, None, other_player, Announce.ToRoom)
        act("$n tells you to keep your voice down...", FALSE, ch, None, other_player, Announce.ToVict)
    """
    msg = msg.replace("$n", ch.name.capitalize())
    msg = msg.replace("$N", vict_obj.name.capitalize())

    if announce_type == Announce.ToRoom:
        ch.location.announce(msg)
        return
    if announce_type == Announce.ToChar:
        ch.msg(msg)
        return
    if announce_type == Announce.ToVict:
        if vict_obj.is_pc:
            if not vict_obj.conditions.has(Sleeping):
                vict_obj.msg(msg)
        return
    if announce_type == Announce.ToNotVict:
        ch.location.announce(msg, exclude=[vict_obj])
        return
