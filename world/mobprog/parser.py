from yapf.yapflib.yapf_api import FormatCode
from evennia import search_object


class MobProgParser:
    """
    Parses a trigger script into valid python code that is then executed via `exec`
    There are two objects interacting within scripts

    1) the object that triggered this script and..
    2) the object this script is attached too.

    valid tokens:

    $i      the first of the names of the object itself.
    $I      the short description of the object itself.
    $n      the name of whomever caused the trigger to happen.
    $N      the name and title of whomever caused the trigger to happen.
    $t      the name of a secondary character target (i.e A smiles at B)
    $T      the short description, or name and title of target (NPC vs PC)
    $r      the name of a random char in the room with the mobile (never == $i)
    $R      the short description, or name and title of the random char

    $j      he,she,it based on sex of $i.
    $e      he,she,it based on sex of $n.
    $E      he,she,it based on sex of $t.
    $J      he,she,it based on sex of $r.

    $k      him,her,it based on sex of $i.
    $m      him,her,it based on sex of $n.
    $M      him,her,it based on sex of $t.
    $K      him,her,it based on sex of $r.

    $l      his,hers,its based on sex of $i.
    $s      his,hers,its based on sex of $n.
    $S      his,hers,its based on sex of $t.
    $L      his,hers,its based on sex of $r.

    $o      the first of the names of the primary object (i.e A drops B)
    $O      the short description of the primary object
    $p      the first of the names of the secondary object (i.e A puts B in C)
    $P      the short description of the secondary object

    $a      a,an based on first character of $o
    $A      a,an based on first character of $p
    """
    def __init__(self, attached_obj, triggerer_obj):
        """
        attached_name: the name of the object the script is attached too
        triggerer_name: the name of the object that triggered the script

        attached_obj can be either mob/room/object
        triggerer_objcan be either pc or npc
        """

        self.attached_obj = attached_obj
        self.triggerer_obj = triggerer_obj

        self.header = """
from evennia import search_object
from world.mobprog.utils import *

ch = search_object("{ch}", use_dbref=True, exact=True)[0]
self = search_object("{vict}", use_dbref=True, exact=True)[0]
""".format(ch=triggerer_obj.dbref, vict=attached_obj.dbref)

    def parse(self, data):
        """
        returns a valid python script 
        that if executed via `exec` it will perform what it needs to do
        """
        data = self._token_replace(data)
        return FormatCode(self.header + data)[0]

    def _token_replace(self, data):
        data = data.replace("$n", 'ch').replace("$i", "vict")
        return data
