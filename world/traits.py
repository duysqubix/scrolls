"""
Much like conditions....
"""
from evennia import search_object
from evennia.utils.utils import inherits_from
from world.conditions import BreathUnderWater, Burning, Condition, Fear, Flying, Intangible


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

    def at_condition(self, caller):
        cur_max_speed = caller.attrs.speed.max
        # halve current max speed
        self.meta['speed_mod'] = -(cur_max_speed // 2 + 1)
        caller.attrs.speed.add_mod(self.meta['speed_mod'])

    def after_condition(self, caller):
        caller.attrs.modifier['speed'].remove(self.meta['speed_mod'])
        caller.attrs.speed.remove_mod(self.meta['speed_mod'])


class DiseaseResistTrait(Trait):
    __conditionname__ = "disease resistance"

    def at_condition(self):
        if self.X is None:
            raise ValueError("disease resistance trait must have X defined")


class DiseasedTrait(Trait):
    __conditionname__ = "diseased"

    def at_condition(self, caller):
        if self.X is None:
            raise ValueError("diseased trait must have X defined")


class FlyerTrait(Trait):
    __conditionname__ = 'flying'

    def at_condition(self, caller):
        if self.X is None:
            raise ValueError("diseased trait must have X defined")
        caller.conditions.add(Flying)

    def after_condition(self, caller):
        caller.conditions.remove(Flying)


class FromBeyondTrait(Trait):
    __conditionname__ = "from beyond"

    def at_condition(self, caller):
        caller.attrs.immunity.value['disease'].append('all')
        caller.attrs.immunity.value['poison'].append('all')
        caller.attrs.immunity.value['condition'].append(Fear)

    def after_condition(self, caller):
        caller.attrs.immunity.value['disease'].remove('all')
        caller.attrs.immunity.value['poison'].remove('all')
        caller.attrs.immunity.value['condition'].remove(Fear)


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

    def at_condition(self, caller):
        caller.attrs.immunity.value[self.imm_type].append(self.imm_obj)

    def after_condition(self, caller):
        caller.attrs.immunity.value[self.imm_type].remove(self.imm_obj)


class IncorporealTrait(Trait):
    __conditionname__ = "incorporeal"

    def at_condition(self, caller):
        caller.conditions.add([Intangible, Flying])

    def after_condition(self, caller):
        caller.conditions.remove([Intangible, Flying])


class NaturalToughnessTrait(Trait):
    __conditionname__ = "natural toughness"

    def init(self):
        if not self.X or not isinstance(self.X, [int, float]):
            raise ValueError('X must be a valid castable int type')

        self.X = int(self.X)


class NaturalWeaponsTrait(Trait):
    """
    character has unique weapons of some kind;
    ex. claws, teeth, etc... adds , TBD, when fighting
    """
    __conditionname__ = "natural weapons"

    def init(self):
        if not self.X:
            raise ValueError(
                "natural weapons traits needs a name when initialized")
        self.X = str(self.X)


class PowerWellTrait(Trait):
    __conditionname__ = 'power well'

    def init(self):
        if not self.X or not isinstance(self.X, [int, float]):
            raise ValueError('X must be valid castable int type')

    def at_condition(self, caller):
        # increase max magicka by X
        caller.attrs.magicka.add_mod(self.X)

    def after_condition(self, caller):
        caller.attrs.magicka.remove_mod(self.X)


class SkeletalTrait(Trait):
    __conditionname__ = 'skeletal'

    def at_condition(self, caller):
        # gain undead trait automatically
        caller.attrs.traits.add(UndeadTrait)
        # immune to burning condition
        caller.attrs.immunity.value['conditions'].append(Burning)

    def after_condition(self, caller):
        caller.attrs.immunity.value['conditions'].remove(Burning)
        caller.attrs.traits.remove(UndeadTrait)


class SilverScarredTrait(Trait):
    __conditionname__ = 'silver scarred'

    def init(self):
        if not self.X or not isinstance(self.X, [float, int]):
            raise ValueError('silver scarred trait requires damage modifier')

        self.X = float(self.X)


class SpellAbsorptionTrait(Trait):
    __conditionname__ = 'spell absorption'

    def init(self):
        if not self.X or not isinstance(self.X, [float, int]):
            raise ValueError('spell absorption requires castable int type')

        self.X = int(self.X)
        if self.X > 10:
            self.X = 10


class StuntedMagickaTrait(Trait):
    __conditionname__ = "stunted magicka"

    def at_condition(self, caller):
        caller.attrs.magicka.rate = 0.0

    def after_condition(self, caller):
        caller.attrs.magicka.rate = 1.0


class SummonedTrait(Trait):
    __conditionname__ = 'summoned'


class SunScarredTrait(Trait):
    __conditionname__ = 'sun scarred'

    def init(self):
        if not self.X or not isinstance(self.X, [int, float]):
            raise ValueError('sun scarred trait requires castable int type')
        self.X = float(self.X)

    def effect(self, caller, **kwargs):
        """ 
        designed to be used when exposed to sun, reduce 
        players SP point by 1
        """
        if self.enabled:
            caller.attrs.change_vital('stamina', -1)


class RegenerationTrait(Trait):
    __conditionname__ = 'regeneration'

    def init(self):
        if not self.X or not isinstance(self.X, [int, float]):
            raise ValueError('regeneration trait requires castable float type')

        self.X = int(self.X)

    def effect(self, caller, **kwargs):
        """ use to heal player X amnt """
        caller.attrs.change_vital('health', 1)


class ResistanceTrait(Trait):
    __conditionname__ = 'resistance'

    # TODO: add resistant types to this trait (resistant types have not been created or defined yet)
    def init(self):
        if not self.X or not isinstance(self.X, [int, float]):
            raise ValueError('resistance trait requires castable float type')

        self.X = float(self.X)


class UndeadTrait(Trait):
    __conditionname__ = 'undead'

    def at_condition(self, caller):
        # immune to disease, poison, aging, fatigue
        # dazed, defened
        caller.attrs.immunity.value['disease'].append('all')
        caller.attrs.immunity.value['poison'].append('all')

    def after_condition(self, caller):
        caller.attrs.immunity.value['disease'].append('all')


class UndyingTrait(Trait):
    __conditionname__ = 'undying'

    def at_condition(self, caller):
        # immune to all disease
        caller.attrs.immunity.value['disease'].append('all')

    def after_condition(self, caller):
        caller.attrs.immunity.value['disease'].append('all')


class UnnaturalSensesTrait(Trait):
    __conditionname__ = 'unatural senses'


class WeaknessTrait(Trait):
    __conditionname__ = 'weakness'

    def init(self):
        if not self.X or not isinstance(self.X, [int, float]):
            raise ValueError("weakness trait requires castable float type")

        self.X = float(self.X)


class TerrifyingTrait(Trait):
    __conditionname__ = 'terrifying'
