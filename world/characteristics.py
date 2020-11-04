

class Characteristic:
    def __init__(self, name, short):
        self.name = str(name)
        self.short = short
        self.base = 0
        self.bonus = 0
        self.favored = False

    def __str__(self):
        return f"Characteristic: <{self.short}>"

    def __repr__(self):
        return str(self)
    

CHARACTERISTICS = [
    Characteristic('strength', 'str'),
    Characteristic('endurance', 'end'),
    Characteristic('agility', 'agi'),
    Characteristic('intelligence', 'int'),
    Characteristic('willpower', 'wp'),
    Characteristic('persuasion', 'prc'),
    Characteristic('perception', 'prs'),
    Characteristic('luck', 'lck')
]