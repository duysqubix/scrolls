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
from world.diseases import ALL_DISEASES  # TODO: actually create that there
from resources.help_entries.help_entry_wrapper import HelpEntryWrapper

HELP_CATEGORY = 'disease'


class RaceSignHelpEntry(HelpEntryWrapper):
    __help_category__ = HELP_CATEGORY


# CODE

diseases = ", ".join([x.name.capitalize() for x in ALL_DISEASES])

# TODO: cut in a main entry text
main_entrytxt = \
f"""
Diseases are contracted from contact with diseased people or
animals, or other creatures that are otherwise filthy, such as
skeevers or mudcrabs. Sometimes diseases can be caught as
the result of traps, poisons, or environmental effects, such as
Corpus.

Common diseases are caught most often from traps, poisons, 
or from fighting diseased animals or people. Common diseases
often start out relatively minor but some progress severely.

Common diseases bear mild social stigma, which can escalate
to disgust and suspicion if it is allowed to develop into later
stages. Given the ease of treating common diseases, only the 
truly destitute and unfaithul are afflicted with what is seen as
their just due.

All common diseases can be cured by using any level Cure 
Disease spell or potion. Any common disease can also be cured
by sincere repentance and piousness at a shrine to one of the
Eight and One. Infected animals typically ignore the effects of
the common diseases they carry.

{diseases}

More help is available on the them by |ghelp <disease>|n
"""
DiseaseHelpEntry.create_main(HELP_CATEGORY, main_entrytxt)

for disease in ALL_DISEASES:
    tmp = DiseaseHelpEntry(disease)

    entry = HelpEntry.objects.find_topicmatch(tmp.key)
    if not entry:
        create_help_entry(**tmp.params())
    else:
        entry[0].entrytext = tmp.entrytext

