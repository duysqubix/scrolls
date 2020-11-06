import random

from world.characteristics import *

__all__ = ('WarriorSign', 'LadySign', 'SteedSign', 'LordSign', 'MageSign',
           'RitualSign', 'ApprenticeSign', 'AtronachSign')


class BirthSign:
    __sign_name__ = ""

    def __init__(self, cursed):
        self.properties = {'effect': {}, 'cursed': {}}
        self.cursed = cursed
        self.init()

    def __str__(self):
        return f"{self.__sign_name__.capitalize()}"

    def __repr__(self):
        return str(self)

    def __format__(self, _format_spec):
        return str(self)

    def init():
        pass

    @property
    def name(self):
        return self.__sign_name__


class NoSign(BirthSign):
    __sign_name__ = "NoSign"


class WarriorSign(BirthSign):
    __sign_name__ = "warrior"

    def init(self):
        self.properties['effect'] = {'stat': [EndChar(bonus=1)]}
        self.properties['cursed'] = {
            'stat': [StrChar(bonus=5), WpChar(bonus=-5)]
        }


class LadySign(BirthSign):
    __sign_name__ = "lady"

    def init(self):
        self.properties['effect'] = {'stat': [PrsChar(bonus=5)]}
        self.properties['cursed'] = {
            'stat': [StrChar(bonus=-5), EndChar(bonus=5)]
        }


class SteedSign(BirthSign):
    __sign_name__ = 'steed'

    def init(self):
        cursed_stat = random.choice([WpChar(bonus=-5), PrcChar(bonus=-5)])
        self.properties['effect'] = {
            'attrs': {
                'speed': 2
            }
        }  # todo do something here
        self.properties['cursed'] = {'stat': [cursed_stat, AgiChar(bonus=5)]}


class LordSign(BirthSign):
    __sign_name__ = "lord"

    def init(self):
        self.properties['effect'] = {'health': {'recover': 2}}
        self.properties['cursed'] = {
            'stat': [EndChar(bonus=5)],
            'trait': {
                'weakness': ('fire', 2)
            }
        }


class MageSign(BirthSign):
    __sign_name__ = "mage"

    def init(self):
        cursed_stat = random.choice(
            [PrcChar(bonus=-5),
             StrChar(bonus=-5),
             PrsChar(bonus=-5)])

        self.properties['effect'] = {'trait': {'power well': 10}}
        self.properties['cursed'] = {
            'trait': {
                'power well': 15
            },
            'stat': [cursed_stat]
        }


class ApprenticeSign(BirthSign):
    __sign_name__ = "apprentice"

    def init(self):
        self.properties['effect'] = {
            'trait': {
                'power well': 25,
                'weakness': ('magic', 3)
            }
        }
        self.properties['cursed'] = {
            'trait': {
                'power well': 25,
                'weakness': ('magic', 1)
            }
        }


class AtronachSign(BirthSign):
    __sign_name__ = "apprentice"

    def init(self):
        self.properties['effect'] = {
            'trait': {
                'power well': 50,
                'spell absorption': 5,
                'stunted magicka': True
            }
        }
        self.properties['cursed'] = {
            'trait': {
                'power well': 25,
                'weakness': ('magic', 1)
            }
        }


class RitualSign(BirthSign):
    __sign_name__ = "ritual"

    def init(self):
        pass
