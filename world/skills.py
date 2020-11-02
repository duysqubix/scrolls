from typeclasses.scripts import Script
from world.storagehandler import StorageHandler
from evennia.utils.utils import lazy_property

class SkillRank:
    __maxrank__ = 6

    def __init__(self, id, name, bonus, desc, cost):
        self.id = id    # numerical id for skill rank
        self.name = name     # human friendly name for rank of skill
        self.bonus = bonus  # bonus applied when using skill
        self.desc = desc    # short description of skill
        self.cost = cost    # cost in XP to move to next level

    def __str__(self):
        return f"{self.name}({self.id})"

    def __repr__(self):
        return str(self)


    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return self.id > other.id

    def __le__(self, other):
        return self.id <= other.id

    def __ge__(self, other):
        return self.id >= other.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return self.id != other.id

    def __add__(self, other):
        other = int(other)
        result = other + self.id
        if result > self.__maxrank__:
            result = self.__maxrank__

        return SkillRanks.get(result)

    def __sub__(self, other):
        if self.id == 0:
            return self
        other = int(other)

        result = self.id-other
        if result < 0:
            return SkillRanks.get(0)

        return SkillRanks.get(result)



class SkillRanks:
    __ranks__ = [
        SkillRank(0, 'untrained', -10, "No knowledge", 0),
        SkillRank(1, 'novice', 0, 'Rudimentary knowledge', 100),
        SkillRank(2, 'apprentice', 10, "Basic proficiency", 200),
        SkillRank(3, 'journeyman', 20, 'Hands on experience and/or some professional training', 300),
        SkillRank(4, 'adept', 30, 'Extensive experience or training', 400),
        SkillRank(5, 'expert', 40, 'Professional level ability', 500),
        SkillRank(6, 'master', 50, 'Complete mastery', 800)
    ]

    def get(rank):
        try:
            rank = int(rank)
            if rank < 0:
                rank = 0
            elif rank > 6:
                rank = 6

            return SkillRanks.__ranks__[rank]
        except ValueError:
            for r in SkillRanks.__ranks:
                if rank.lower() == r.name:
                    return r

        except TypeError:
            if isinstance(rank, SkillRank):
                return rank
            return None

        return None

class GoverningSkill:
    def __init__(self, name, governing_chars):
        self.name = name

        if not isinstance(governing_chars, list):
            governing_chars = [governing_chars]
        self.governing = governing_chars

    def __str__(self):
        return f"GoverningSkill: <{self.name}>"

    def __repr__(self):
        return str(self)


class GoverningSkills:
    __skills__ = {
    'acrobatics': GoverningSkill('acrobatics', ['str, agi']),
    'alchemy': GoverningSkill('alchemy', ['int']),
    'alteration': GoverningSkill('alteration', ['wp']),
    'athletics': GoverningSkill('athletics', ['str', 'agi']),
    'command': GoverningSkill('command', ['str', 'int', 'prs']),
    'commerce': GoverningSkill('commerce', ['prs']),
    'conjuration': GoverningSkill('conjuration', ['wp']),
    'decieve': GoverningSkill('decieve', ['prs']),
    'destruction': GoverningSkill('destruction', ['wp']),
    'enchant': GoverningSkill('enchant', ['int']),
    'evade': GoverningSkill('evade', ['agi']),
    'illusion': GoverningSkill('illusion', ['wp']),
    'investigate': GoverningSkill('investigate', ['int', 'prc']),
    'logic': GoverningSkill('logic', ['int', 'prc']),
    'lore': GoverningSkill('lore', ['int']),
    'mysticism': GoverningSkill('mysticism', ['wp']),
    'navigate': GoverningSkill('navigate', ['int', 'prc']),
    'observe': GoverningSkill('observe', ['prc']),
    'persuade': GoverningSkill('persuade', ['str', 'prs']),
    'restoration': GoverningSkill('restoration', ['wp']),
    'ride': GoverningSkill('ride', ['agi']),
    'stealth': GoverningSkill('stealth', ['agi', 'prc']),
    'subterfuge': GoverningSkill('subterfuge', ['agi', 'int', 'prs']),
    'survival': GoverningSkill('survival', ['int', 'prc'])
    }

    def get(key):
        if key not in GoverningSkills.__skills__:
            return None
        return GoverningSkills.__skills__[key]

class Skill:
    def __init__(self, name, rank, governing_skill):
        self.name = name

        self.rank = SkillRanks.get(rank)
        if self.rank is None:
            self.rank = SkillRanks.get('novice')

        self.governing_skill = governing_skill

    def __str__(self):
        return f"Skill: <{self.name}>"

    def __repr__(self):
        return str(self)


class SkillDBHandler(StorageHandler):
    __attr_name__ = 'skills'


class SkillDB(Script):


    @lazy_property
    def skills(self):
        return SkillDBHandler(self)

    def at_object_creation(self):
        self.db.skills = {}

    def add(self, skill: Skill):
        self.db.skills[skill.name] = skill
        self.skills.update()

    def __getitem__(self, key):
        if key in self.skills.all():
            return self.db.skills[key]
        return None
