#
#
# Custom Help entries for birthsigns
#
#

# HEADER

from resources.help_entries.help_entry_wrapper import HelpEntryWrapper
from evennia.utils.utils import dedent
from world.birthsigns import ALL_BIRTHSIGNS
from evennia import create_help_entry
from evennia.help.models import HelpEntry
from evennia.utils import dedent

HELP_CATEGORY = 'birthsign'


class BirthSignHelpEntry(HelpEntryWrapper):
    __help_category__ = HELP_CATEGORY


# CODE

main_entrytxt = \
"""
   \"The fates of mortals lies in the pattern of the stars\"
      - anonymous (1E122)

Birthsigns determine key traits and abilities that are
bestowed on a character when they are born. The Cyrodillic empire
recognizes three main groups under which all signs are categorized.

The signs of the warrior:
    |rWarrior|n
    |rLady|n
    |rSteed|n
    |rLord|n

The signs of the mage:
    |bMage|n
    |bApprentice|n
    |bAtronach|n
    |bRitual|n

The signs of the thief:
    |yThief|n
    |yLover|n
    |yShadow|n
    |yTower|n

The gods are fickle entities sometimes bestowing powerful capabilities
to their subjects. However, this power comes at a cost.
"""

BirthSignHelpEntry.create_main(HELP_CATEGORY, main_entrytxt)

for sign in ALL_BIRTHSIGNS:
    tmp = BirthSignHelpEntry(sign)

    entry = HelpEntry.objects.find_topicmatch(tmp.key)
    if not entry:
        create_help_entry(**tmp.params())
    else:
        entry[0].entrytext = tmp.entrytext
