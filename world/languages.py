from pathlib import Path
from world.globals import Untrained, Novice, Apprentice, Journeyman, Adept, Expert, Master
from evennia.contrib.rplanguage import _PHONEMES, _GRAMMAR, _VOWELS, available_languages, add_language, _LANGUAGE_HANDLER

_WORDS_CONTENTS = None

if not _WORDS_CONTENTS:
    with open(Path('resources/common_english.txt').absolute(), 'r') as f:
        _WORDS_CONTENTS = f.read().split('\n')


class _Language:
    __lang_name__ = ""

    def __init__(self) -> None:
        self.phonemes = _PHONEMES
        self.grammar = _GRAMMAR
        self.word_length_variance = 0
        self.noun_translate = False,
        self.noun_prefix = ""
        self.noun_postfix = ""
        self.vowels = _VOWELS
        self.manual_translations = None

        self._auto_translations = _WORDS_CONTENTS

        self.define_language()

    def define_language(self):
        raise NotImplementedError("must define how language is set up")

    def add(self, override=False):

        if self.__lang_name__ not in available_languages() or override:
            add_language(key=self.__lang_name__,
                         phonemes=self.phonemes,
                         grammar=self.grammar,
                         word_length_variance=self.word_length_variance,
                         noun_translate=self.noun_translate,
                         noun_prefix=self.noun_prefix,
                         noun_postfix=self.noun_postfix,
                         vowels=self.vowels,
                         manual_translations=self.manual_translations,
                         auto_translations=self._auto_translations,
                         force=True)

    def delete(self):
        """
        meant to only be access via api, deletes language
        """
        _ = available_languages()  # to init language handler
        handler = _LANGUAGE_HANDLER
        if self.__lang_name__ in available_languages():
            del handler.db.language_storage[self.__lang_name__]


class Tamrielic(_Language):
    """
    Tamrielic, sometimes referred to as the Common Tongue, is the standard 
    language spoken throughout The Elder Scrolls. It is the basic lingua 
    franca of the Cyrodilic empire and its citizens, but is most widely 
    spoken by humans.
    """
    __lang_name__ = 'tamrielic'

    def define_language(self):
        self.phonemes = _PHONEMES
        self.grammar = _GRAMMAR
        self.word_length_variance = 0
        self.noun_translate = False,
        self.noun_prefix = ""
        self.noun_postfix = ""
        self.vowels = _VOWELS
        self.manual_translations = None


class Aldmeris(_Language):
    """
    The Aldmeri Language, known as Aldmeris is one of Tamriel's oldest languages and is spoken by the Altmer. It is structurally similar to Ehlnofex but 
    more consistent in grammatical syntax and phonetic meaning. Most other languages, such as Dunmeri, Bosmeri, and Nedic, stem from the Aldmeri Language 
    and the namesake of most places in Tamriel, including Tamriel itself, are based on Aldmeri words.
    """
    __lang_name__ = "aldmerish"

    def define_language(self):
        self.phonemes = "eu ae ai qu d h l s th n m v w fe kh ll ii nn ia ga gi h ly u t r y a e am ie"

        self.vowels = "aeiou"
        self.grammar = "v vv vc ccv cvccv cvcv cvccvc cvcvcc "
        self.word_length_variance = 3
        self.noun_postfix = "diil"
        self.manual_translations = {
            'dragon': 'aka',
            'first': 'ald',
            'elder': 'at',
            'high': 'alt',
            'old': 'ald',
            'beast': 'bet',
            'green': 'bos',
            'forest': 'bos',
            'stone': 'bal',
            'changed': 'chi',
            'dark': 'dun',
            'cursed': 'dun',
            'deep': 'dwe',
            'high': 'esh',
            'sewers': 'halsoriel',
            'fire': 'molag',
            'newcomer': 'nebarra',
            'city': 'nium',
            'town': 'nium',
            'orc': 'orsi',
            'aedra': 'aedra',
            'aedroth': 'aedroth',
            'daedra': 'daedra',
            'daedroth': 'daedroth'
        }


class Orcish(_Language):
    """
    The Orcish language is one of the more gutteral sounds of Tamriel. Spoken by the orcs of Tamriel their exists many dialects throughout all the
    warring tribes. Most scholars do not recognize orcish as an official language becuase of its primitive foundation.
    """
    __lang_name__ = "orcish"

    def define_language(self):
        self.phonemes = "a g kh rz k r z th t m ush am oo d ug zz gg eg ag oz uu us uth zu rul ol ru hz ri au ai kr gog rzn lag"
        self.vowels = "auo"
        self.grammar = "ccvvcc ccvcc vccv vccvccvcc ccvvcvcc cvcccvcc cvcc vccccvc vcvcc cvccccv ccvcvccc cvccvcc cvcvcvcc cvcccvc ccccvc vcvvc vccvcvc ccvcv cvccvc cvccccvc cvccc cvccvcvc cvvcvc ccvccvccvc vcccvc vcvcvc ccvccvc cvccv cvcvccvcc cvcvcvc cvcvcv cvcccv cvcvcc cvcvcccc vcvccvc vccvc ccvcvc cvccccc cvcccccc"
        self.word_length_variance = 2


VALID_LANGUAGES = {
    Tamrielic.__lang_name__: Tamrielic,
    Aldmeris.__lang_name__: Aldmeris,
    Orcish.__lang_name__: Orcish
}


class LanguageSkill:
    untrained = Untrained(level=0.0)
    novice = Novice(level=0.1)
    apprentice = Apprentice(level=0.3)
    journeyman = Journeyman(level=0.5)
    adept = Adept(level=0.7)
    expert = Expert(level=0.9)
    master = Master(level=1.0)
