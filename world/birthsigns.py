from world.traits import PowerWellTrait, SpellAbsorptionTrait, StuntedMagickaTrait, WeaknessTrait
import evennia
import random

from world.characteristics import *

__all__ = ('WarriorSign', 'LadySign', 'SteedSign', 'LordSign', 'MageSign',
           'RitualSign', 'ApprenticeSign', 'AtronachSign', 'change_birthsign')


class BirthSign:
    __sign_name__ = ""

    def __init__(self, cursed=False):
        self.properties = {'effect': {}, 'cursed': {}}
        self.cursed = cursed
        self.init()

    def __str__(self):
        cursed = "" if not self.cursed else "|r*|n"
        return f"{cursed}{self.__sign_name__.capitalize()}"

    def __repr__(self):
        return str(self)

    def __format__(self, _format_spec):
        return str(self)

    def __eq__(self, other):
        return self.__sign_name__ == other.__sign_name__

    def init(self):
        pass

    @property
    def name(self):
        return self.__sign_name__


class NoSign(BirthSign):
    __sign_name__ = "NoSign"


class WarriorSign(BirthSign):
    __sign_name__ = "warrior"

    def init(self):
        self.properties['effect'] = {'stats': [EndChar(bonus=1)]}
        self.properties['cursed'] = {
            'stats': [StrChar(bonus=5), WpChar(bonus=-5)]
        }


class LadySign(BirthSign):
    __sign_name__ = "lady"

    def init(self):
        self.properties['effect'] = {'stats': [PrsChar(bonus=5)]}
        self.properties['cursed'] = {
            'stats': [StrChar(bonus=-5), EndChar(bonus=5)]
        }


class SteedSign(BirthSign):
    __sign_name__ = 'steed'

    def init(self):
        cursed_stats = random.choice([WpChar(bonus=-5), PrcChar(bonus=-5)])
        self.properties['effect'] = {
            'attrs': {
                'speed': 2
            }
        }  # todo do something here
        self.properties['cursed'] = {'stats': [cursed_stats, AgiChar(bonus=5)]}


class LordSign(BirthSign):
    __sign_name__ = "lord"

    def init(self):
        self.properties['effect'] = {'health': {'recover': 2}}
        self.properties['cursed'] = {
            'stats': [EndChar(bonus=5)],
            'traits': [(WeaknessTrait, 2, 'fire')]
        }


class MageSign(BirthSign):
    __sign_name__ = "mage"

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
    __sign_name__ = "apprentice"

    def init(self):
        self.properties['effect'] = {
            'traits': [(PowerWellTrait, 25, None), (WeaknessTrait, 3, 'magic')]
        }
        self.properties['cursed'] = {
            'traits': [(PowerWellTrait, 25, None), (WeaknessTrait, 1, 'magic')]
        }


class AtronachSign(BirthSign):
    __sign_name__ = "apprentice"

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
    __sign_name__ = "ritual"

    def init(self):
        pass


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
                        print(traits, trait)
                        trait_cls, X, Y = trait
                        caller.traits.remove(trait_cls)

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