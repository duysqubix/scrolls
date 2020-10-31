class SkillRank:
    def __init__(self, id, name, bonus, desc):
        self.id = id
        self.name = name
        self.bonus = bonus
        self.desc = desc

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


SKILL_RANKS = {
    'untrained':
    SkillRank(0, 'untrained', -10, "No knowledge"),
    'novice':
    SkillRank(1, 'novice', 0, 'Rudimentary knowledge'),
    'apprentice':
    SkillRank(2, 'apprentice', 10, "Basic proficiency"),
    'journeyman':
    SkillRank(3, 'journeyman', 20,
              'Hands on experience and/or some professional training'),
    'adept':
    SkillRank(4, 'adept', 30, 'Extensive experience or training'),
    'expert':
    SkillRank(5, 'expert', 40, 'Professional level ability'),
    'master':
    SkillRank(6, 'master', 50, 'Complete mastery')
}
