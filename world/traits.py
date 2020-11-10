"""
Much like conditions....
"""
from evennia import search_object
from evennia.utils.utils import inherits_from
from world.conditions import BreathUnderWater, Condition, Fear, Flying, Intangible


class Trait(Condition):
    pass


class AmphibiousTrait(Trait):
    __conditionname__ = "ambphibious"

    def at_condition(self, caller):
        caller.conditions.add(BreathUnderWater)


class BoundTrait(Trait):
    __conditionname__ = "bound"

    def __init__(self, caller_id, master_id):
        super().__init__(caller_id, X=None)
        self.master_id = master_id

    @property
    def master(self):
        dbref = f"#{self.master_id}"
        obj = search_object(dbref, exact=True, use_dbref=True)
        if not obj:
            return None
        return obj[0]


class CrawlingTrait(Trait):
    __conditionname__ = "crawling"

    def at_condition(self):
        cur_max_speed = self.caller.attrs.speed.max
        # halve current max speed
        self.meta['speed_mod'] = -(cur_max_speed // 2 + 1)
        self.caller.attrs.speed.add_mod(self.meta['speed_mod'])

    def after_condition(self):
        self.caller.attrs.modifier['speed'].remove(self.meta['speed_mod'])
        self.caller.attrs.speed.remove_mod(self.meta['speed_mod'])


class DiseaseResistTrait(Trait):
    __conditionname__ = "disease resistance"

    def at_condition(self):
        if self.X is None:
            raise ValueError("disease resistance trait must have X defined")


class DiseasedTrait(Trait):
    __conditionname__ = "diseased"

    def at_condition(self):
        if self.X is None:
            raise ValueError("diseased trait must have X defined")


class FlyerTrait(Trait):
    __conditionname__ = 'flying'

    def at_condition(self):
        if self.X is None:
            raise ValueError("diseased trait must have X defined")
        self.caller.conditions.add(Flying)

    def after_condition(self):
        self.caller.conditions.remove(Flying)


class FromBeyondTrait(Trait):
    __conditionname__ = "from beyond"

    def at_condition(self):
        self.caller.attrs.immunity.value['disease'].append('all')
        self.caller.attrs.immunity.value['poison'].append('all')
        self.caller.attrs.immunity.value['condition'].append(Fear)

    def after_condition(self):
        self.caller.attrs.immunity.value['disease'].remove('all')
        self.caller.attrs.immunity.value['poison'].remove('all')
        self.caller.attrs.immunity.value['condition'].remove(Fear)


class ImmunityTrait(Trait):

    __conditionname__ = "immunity"

    def init(self):
        """
        ex:
        mytrait = Immunity(X={'disease': RockJoint})
        """
        self.multiple = True
        if not self.X or not inherits_from(self.X, dict):
            raise ValueError("X must be valid dictionary")

        self.immunity_map = {
            'disease': 'world.diseases.Disease',
            'poison': 'world.poisons.Poison',
            'condition': 'world.conditions.Condition'
        }
        self.imm_type = list(self.X.keys())[0]
        self.imm_obj = self.X[self.imm_type]
        obj_class_type = self.immunity_map[self.imm_type]
        print(obj_class_type)
        if not inherits_from(self.imm_obj, obj_class_type):
            raise ValueError("X must be a valid condition, disease, or poison")

    def at_condition(self):
        self.caller.attrs.immunity.value[self.imm_type].append(self.imm_obj)

    def after_condition(self):
        self.caller.attrs.immunity.value[self.imm_type].remove(self.imm_obj)


class IncorporealTrait(Trait):
    __conditionname__ = "incorporeal"

    def at_condition(self):
        self.caller.conditions.add([Intangible, Flying])
