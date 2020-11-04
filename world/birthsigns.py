import random

__all__ = (
    'WarriorSign',
    'LadySign',
    'SteedSign',
    'LordSign'
)

class BirthSign:
    __sign_name__ = ""

    def __init__(self, cursed):
        self.properties = {
            'effect': {},'cursed': {}
        }
        self.cursed = cursed
        self.init()

    def __str__(self):
        return f"Birthsign: The {self.__sign_name__.capitalize()}"

    def __repr__(self):
        return str(self)

    def init():
        pass

    @property
    def name(self):
        return self.__sign_name__

class WarriorSign(BirthSign):
    __sign_name__ = "warrior"

    def init(self):
        self.properties['effect'] = {'stat': {'end': {'bonus': 1}}}
        self.properties['cursed'] = {'stat': {'str': 5, 'wp': -5}}


class LadySign(BirthSign):
    __sign_name__ = "lady"

    def init(self):
        self.properties['effect'] = {'stat': {'prs': {'bonus': 5}}}
        self.properties['cursed'] = {'stat': {'str': -5, 'end': 5}}

class SteedSign(BirthSign):
    __sign_name__ = 'steed'

    def init(self):
        cursed_stat = random.choice(['wp', 'prc'])
        self.properties['effect'] = {'attrs': {'speed': 2}}
        self.properties['cursed'] = {'stat': {cursed_stat: -5, 'agi': 5}}


class LordSign(BirthSign):
    __sign_name__ = "lord"

    def init(self):
        self.properties['effect'] = {'health': {'recover': 2}}
        self.properties['cursed'] = {'stat': {'end': 5}, 'trait': {'weakness': ('fire', 2)}}
