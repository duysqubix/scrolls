#
#
# Custom Help entries for races
#
#

# HEADER

from os import stat
from resources.help_entries.birthsigns import HELP_CATEGORY
from evennia import create_help_entry
from evennia.help.models import HelpEntry
from evennia.utils import dedent
from world.races import PLAYABLE_RACES
from resources.help_entries.help_entry_wrapper import HelpEntryWrapper

HELP_CATEGORY = 'race'


class RaceSignHelpEntry(HelpEntryWrapper):
    __help_category__ = HELP_CATEGORY


# CODE

races = ", ".join([x.name.capitalize() for x in PLAYABLE_RACES])

main_entrytxt = \
f"""
Tamerial is a place of wonder and mystery. Swaths of strange and mysterious creatures
call Mundus home, however only some are intelligent enough to understand their place
in the universe. They go about their daily lives, eating, drinking, and adventuring.

These are the playable races of Mundus.

{races}

more help is available on the them by |ghelp <race>|n
"""

entry = RaceSignHelpEntry.create_main(HELP_CATEGORY, main_entrytxt)

for race in PLAYABLE_RACES:
    tmp = RaceSignHelpEntry(race)

    # add stats for race
    stats, traits = tmp.obj.formatted()

    tmp.entrytext += f"\n\nStats: {stats}\n"
    tmp.entrytext += f"\nTraits: {traits}"

    entry = HelpEntry.objects.find_topicmatch(tmp.key)
    if not entry:
        create_help_entry(**tmp.params())
    else:
        entry[0].entrytext = tmp.entrytext
