from pathlib import Path
from world.globals import Untrained, Novice, Apprentice, Journeyman, Adept, Expert, Master
from evennia.contrib import rplanguage

_WORDS_CONTENTS = None

if not _WORDS_CONTENTS:
    with open(Path('resources/common_english.txt').absolute(), 'r') as f:
        _WORDS_CONTENTS = f.read().split('\n')


class Language:
    __lang_name__ = ""

    def __init__(self) -> None:
        self.phonemes = None
        self.grammar = None
        self.word_length_variance = None
        self.noun_translate = None
        self.noun_prefix = None
        self.noun_postfix = None
        self.vowels = None
        self.manual_translations = None

        self._auto_translations = _WORDS_CONTENTS

        self.define_language()

    def define_language(self):
        raise NotImplementedError("must define how language is set up")

    def add(self):

        if self.__lang_name__ not in rplanguage.available_languages():
            rplanguage.add_language(
                key=self.__lang_name__,
                phonemes=self.phonemes,
                grammar=self.grammar,
                word_length_variance=self.word_length_variance,
                noun_translate=self.noun_translate,
                noun_prefix=self.noun_prefix,
                noun_postfix=self.noun_postfix,
                vowels=self.vowels,
                manual_translations=self.manual_translations,
                auto_translations=self._auto_translations)

    def delete(self):
        """
        meant to only be access via api, deletes language
        """
        _ = rplanguage.available_languages()  # to init language handler
        handler = rplanguage._LANGUAGE_HANDLER
        if self.__lang_name__ in rplanguage.available_languages():
            del handler.db.language_storage[self.__lang_name__]


class Tamrielic(Language):
    """
    Tamrielic, sometimes referred to as the Common Tongue, is the standard 
    language spoken throughout The Elder Scrolls. It is the basic lingua 
    franca of the Cyrodilic empire and its citizens, but is most widely 
    spoken by humans.
    """
    __lang_name__ = 'tamrielic'

    def define_language(self):
        self.phonemes = rplanguage._PHONEMES
        self.grammar = rplanguage._GRAMMAR
        self.word_length_variance = 0
        self.noun_translate = False,
        self.noun_prefix = ""
        self.noun_postfix = ""
        self.vowels = rplanguage._VOWELS
        self.manual_translations = None


class Aldmeris(Language):
    """
    The Aldmeri Language, known as Aldmeris is one of Tamriel's oldest languages and is spoken by the Altmer. It is structurally similar to Ehlnofex but more consistent in grammatical syntax and phonetic meaning. Most other languages, such as Dunmeri, Bosmeri, and Nedic, stem from the Aldmeri Language and the namesake of most places in Tamriel, including Tamriel itself, are based on Aldmeri words.
    """
    __lang_name__ = "aldmerish"

    def define_language(self):
        self.phonemes = "oi oh ee ae aa eh ah ao aw ay er ey ow ia ih iy" \
                        "oy ua uh uw y pb t d f v t dh s z sh zh ch jh k" \
                        "ng g m n l r w",
        self.vowels = "eaoiuy"
        self.grammar = "v vv vvc vcc vvcc cvvc vccv vvccv vcvccv vvccvvcc "\
                        "ng g m n l r w",
        self.word_length_variance = 1
        self.noun_postfix = "'la"
        self.manual_translations = {
            "the": "y'e",
            "we": "uyi",
            "she": "semi",
            "he": "emi",
            "you": "do",
            'me': 'mi',
            'i': 'me',
            'be': "hy'e",
            'and': 'y'
        }


VALID_LANGUAGES = {
    Tamrielic.__lang_name__: Tamrielic,
    Aldmeris.__lang_name__: Aldmeris
}


class LanguageSkill:
    untrained = Untrained(level=0.0)
    novice = Novice(level=0.1)
    apprentice = Apprentice(level=0.3)
    journeyman = Journeyman(level=0.5)
    adept = Adept(level=0.7)
    expert = Expert(level=0.9)
    master = Master(level=1.0)
