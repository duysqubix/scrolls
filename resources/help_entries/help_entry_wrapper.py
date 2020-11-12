from evennia.utils import dedent, wrap
from evennia.help.models import HelpEntry
from evennia import create_help_entry


class HelpEntryWrapper:
    __help_category__ = ""

    def __init__(self, obj):
        try:
            self.obj = obj()
        except Exception:
            self.obj = obj
        self.key = f"{self.__help_category__} {self.obj.__obj_name__}"
        self.entrytext = wrap(dedent(self.obj.__doc__), width=80)
        self.category = f"{self.__help_category__}-{self.obj.__help_category__.capitalize()}-category"
        self.locks = "view:all()"
        self.aliases = [self.obj.__obj_name__]

    def create_main(key, entrytext):
        entry = HelpEntry.objects.find_topicmatch(key)

        if not entry:
            create_help_entry(key,
                              entrytext=entrytext,
                              locks="view:all()",
                              aliases=None)
        else:
            entry[0].entrytext = entrytext

    def params(self):
        return {
            'key': self.key,
            'entrytext': self.entrytext,
            'category': self.category,
            'locks': self.locks,
            'aliases': self.aliases
        }
