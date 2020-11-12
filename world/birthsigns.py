from world.traits import PowerWellTrait, RunningOutOfLuckTrait, SpellAbsorptionTrait, StuntedMagickaTrait, WeaknessTrait
import evennia
import random

from world.characteristics import *

__all__ = ('WarriorSign', 'LadySign', 'SteedSign', 'LordSign', 'MageSign',
           'RitualSign', 'ApprenticeSign', 'AtronachSign', 'change_birthsign',
           'ThiefSign', 'LoverSign', 'ShadowSign', 'TowerSign')


class BirthSign:
    __obj_name__ = ""
    __help_category__ = ""

    def __init__(self, cursed=False):
        self.properties = {'effect': {}, 'cursed': {}}
        self.cursed = cursed
        self.init()

    def __str__(self):
        cursed = "" if not self.cursed else "|r*|n"
        return f"{cursed}{self.__obj_name__.capitalize()}"

    def __repr__(self):
        return str(self)

    def __format__(self, _format_spec):
        return str(self)

    def __eq__(self, other):
        return self.__obj_name__ == other.__obj_name__

    def init(self):
        pass

    @property
    def name(self):
        return self.__obj_name__


class NoSign(BirthSign):
    __obj_name__ = "NoSign"


class WarriorSign(BirthSign):
    """
    The Warrior is the first Guardian Constellation and he protects his 
    charges during their Seasons. The Warrior’s own season is Last Seed when 
    his Strength is needed for the harvest. His Charges are the Lady, the 
    Steed, and the Lord. Those born under the sign of the Warrior are 
    skilled with weapons of all kinds, but prone to short tempers.
    """
    __obj_name__ = "warrior"
    __help_category__ = "warrior"

    def init(self):
        self.properties['effect'] = {'stats': [EndChar(bonus=1)]}
        self.properties['cursed'] = {
            'stats': [StrChar(bonus=5), WpChar(bonus=-5)]
        }


class LadySign(BirthSign):
    """
    The Lady is one of the Warrior’s Charges and her Season is Heartfire. 
    Those born under the sign of the Lady are kind and tolerant.
    """
    __obj_name__ = "lady"
    __help_category__ = "warrior"

    def init(self):
        self.properties['effect'] = {'stats': [PrsChar(bonus=5)]}
        self.properties['cursed'] = {
            'stats': [StrChar(bonus=-5), EndChar(bonus=5)]
        }


class SteedSign(BirthSign):
    """
    The Steed is one of the Warrior’s Charges, and her Season is Mid Year. 
    Those born under the sign of the Steed are impatient and always hurrying 
    from one place to another.
    """
    __obj_name__ = 'steed'
    __help_category__ = "warrior"

    def init(self):
        cursed_stats = random.choice([WpChar(bonus=-5), PrcChar(bonus=-5)])
        self.properties['effect'] = {
            'attrs': {
                'speed': 2
            }
        }  # todo do something here
        self.properties['cursed'] = {'stats': [cursed_stats, AgiChar(bonus=5)]}


class LordSign(BirthSign):
    """
    The Lord’s Season is First Seed and he oversees all of Tamriel during 
    the planting. Those born under the sign of the Lord are stronger and 
    healthier than those born under other signs.
    """
    __obj_name__ = "lord"
    __help_category__ = "warrior"

    def init(self):
        self.properties['effect'] = {'health': {'recover': 2}}
        self.properties['cursed'] = {
            'stats': [EndChar(bonus=5)],
            'traits': [(WeaknessTrait, 2, 'fire')]
        }


class MageSign(BirthSign):
    """
    The Mage is a Guardian Constellation whose Season is Rain’s Hand when 
    magicka was first used by men. His Charges are the Apprentice, the 
    Golem, and the Ritual. Those born under the Mage have more magicka and 
    talent for all kinds of spellcasting, but are often arrogant and 
    absent-minded.
    """
    __obj_name__ = "mage"
    __help_category__ = "mage"

    def init(self):
        cursed_stats = random.choice(
            [PrcChar(bonus=-5),
             StrChar(bonus=-5),
             PrsChar(bonus=-5)])

        self.properties['effect'] = {'traits': [(PowerWellTrait, 10, None)]}
        self.properties['cursed'] = {
            'traits': [(PowerWellTrait, 15, None)],
            'stats': [cursed_stats]
        }


class ApprenticeSign(BirthSign):
    """
    The Apprentice’s Season is Sun’s Height. Those born under the sign of 
    the apprentice have a special affinity for magick of all kinds, but are 
    more vulnerable to magick as well.
    """
    __obj_name__ = "apprentice"
    __help_category__ = "mage"

    def init(self):
        self.properties['effect'] = {
            'traits': [(PowerWellTrait, 25, None), (WeaknessTrait, 3, 'magic')]
        }
        self.properties['cursed'] = {
            'traits': [(PowerWellTrait, 25, None), (WeaknessTrait, 1, 'magic')]
        }


class AtronachSign(BirthSign):
    """
    The Atronach (often called the Golem) is one of the Mage’s Charges. Its 
    season is Sun’s Dusk. Those born under this sign are natural sorcerers 
    with deep reserves of magicka, but they cannot generate magicka of their 
    own.
    """
    __obj_name__ = "atronach"
    __help_category__ = "mage"

    def init(self):
        self.properties['effect'] = {
            'traits': [(PowerWellTrait, 50, None),
                       (SpellAbsorptionTrait, 5, None),
                       (StuntedMagickaTrait, None, None)]
        }
        self.properties['cursed'] = {
            'traits': [(PowerWellTrait, 25, None), (WeaknessTrait, 1, 'magic')]
        }


class RitualSign(BirthSign):
    """
    The Ritual is one of the Mage’s Charges and its Season is Morning Star. 
    Those born under this sign have a variety of abilities depending on the 
    aspects of the moons and the Divines.
    """
    __obj_name__ = "ritual"
    __help_category__ = "mage"

    def init(self):
        pass


class ThiefSign(BirthSign):
    """
    The Thief is the last Guardian Constellation, and her Season is the 
    darkest month of Evening Star. Her Charges are the Lover, the Shadow, 
    and the Tower. Those born under the sign of the Thief are not typically 
    thieves, though they take risks more often and only rarely come to harm. 
    They will run out of luck eventually, however, and rarely live as long 
    as those born under other signs.
    """
    __obj_name__ = "thief"
    __help_category__ = "thief"

    def init(self):
        self.properties['cursed'] = {
            'traits': [(RunningOutOfLuckTrait, None, None)]
        }


class LoverSign(BirthSign):
    """
    The Lover is one of the Thief ’s Charges and her season is Sun’s Dawn. 
    Those born under the sign of the Lover are graceful and passionate.
    """
    __obj_name__ = 'lover'
    __help_category__ = "thief"

    def init(self):
        cursed_stats = random.choice([WpChar(bonus=-5), StrChar(bonus=-5)])

        self.properties['effect'] = {'stats': [AgiChar(bonus=5)]}
        self.properties['cursed'] = {'stats': [cursed_stats, PrsChar(bonus=5)]}


class ShadowSign(BirthSign):
    """
    The Shadow’s Season is Second Seed. The Shadow grants those born under 
    her sign the ability to hide in shadows.
    """

    __obj_name__ = 'shadow'
    __help_category__ = "thief"

    def init(self):
        cursed_stats = random.choice([PrsChar(bonus=-5), StrChar(bonus=-5)])

        self.properties['effect'] = {'power': ['moonshadow']}
        self.properties['cursed'] = {'stats': [cursed_stats, PrcChar(bonus=5)]}


class TowerSign(BirthSign):
    """
    The Tower is one of the Thief ’s Charges and its Season is Frostfall. 
    Those born under the sign of the Tower have a knack for finding gold and 
    can open locks of all kinds.
    """

    __obj_name__ = 'tower'
    __help_category__ = "thief"

    def init(self):
        cursed_stats = random.choice([WpChar(bonus=-5), StrChar(bonus=-5)])

        self.properties['effect'] = {
            'power': ['treasure_seeker'],
            'stats': [PrcChar(bonus=5)]
        }
        self.properties['cursed'] = {'stats': [cursed_stats, AgiChar(bonus=5)]}


ALL_BIRTHSIGNS = [
    WarriorSign, LadySign, SteedSign, LordSign, MageSign, ApprenticeSign,
    AtronachSign, RitualSign, ThiefSign, LoverSign, ShadowSign, TowerSign
]


def change_birthsign(caller, birthsign):
    if caller.attrs.birthsign.value == birthsign:
        caller.msg("you already are born under the {birthsign}")
        return

    try:
        cursed = caller.attrs.birthsign.value.cursed
    except AttributeError:
        cursed = False

    if not (birthsign == NoSign()):
        # remove effects of current birthsign
        for type_, values in caller.attrs.birthsign.value.properties.items():
            for k, v in values.items():
                if k == 'stats':
                    stats = v
                    if type_ == 'cursed' and not cursed:
                        continue

                    for stat in stats:
                        cur_stat = caller.stats.get(stat.short)
                        new_stat = cur_stat - stat
                        caller.stats.set(stat.short, new_stat)
                elif k == 'traits':
                    traits = v

                    if type_ == 'cursed' and not cursed:
                        continue

                    for trait in traits:
                        # add each trait
                        print(traits, ', trait is', trait)
                        trait_cls, X, Y = trait
                        caller.traits.remove(trait)

                elif k == 'powers':
                    pass

    # add effects of new birthsign
    for type_, values in birthsign.properties.items():
        for k, v in values.items():
            if k == 'stats':
                stats = v
                if type_ == 'cursed' and not cursed:
                    continue

                for stat in stats:
                    cur_stat = caller.stats.get(stat.short)
                    new_stat = cur_stat + stat
                    caller.stats.set(stat.short, new_stat)
            elif k == 'traits':
                traits = v

                if type_ == 'cursed' and not cursed:
                    continue

                for trait in traits:
                    # add each trait
                    trait_cls, X, Y = trait
                    caller.traits.add(trait)

            elif k == 'powers':
                pass

    # finally change birthsign of caller
    birthsign.cursed = cursed
    caller.attrs.birthsign.value = birthsign