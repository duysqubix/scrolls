#
#
# Custom Help entries for diseases
#
#

# HEADER

from os import stat
from resources.help_entries.birthsigns import HELP_CATEGORY
from evennia import create_help_entry
from evennia.help.models import HelpEntry
from evennia.utils import dedent
from world.diseases import ALL_DISEASES
from resources.help_entries.help_entry_wrapper import HelpEntryWrapper

HELP_CATEGORY = 'disease'


class RaceSignHelpEntry(HelpEntryWrapper):
    __help_category__ = HELP_CATEGORY


# CODE

diseases = ", ".join([x.name.capitalize() for x in ALL_DISEASES])

main_entrytxt = \
f"""

{diseases}

more help is available on the them by |ghelp <disease>|n
"""
DiseaseHelpEntry.create_main(HELP_CATEGORY, main_entrytxt)

for sign in ALL_DISEASES:
    tmp = DiseaseHelpEntry(disease)

    entry = HelpEntry.objects.find_topicmatch(tmp.key)
    if not entry:
        create_help_entry(**tmp.params())
    else:
        entry[0].entrytext = tmp.entrytext

