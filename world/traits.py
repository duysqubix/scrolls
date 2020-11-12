"""
Much like conditions....
"""
from collections import namedtuple
from evennia import search_object
from evennia.utils.utils import inherits_from
from world.conditions import BreathUnderWater, Burning, Condition, DarkSight, Fear, Flying, Intangible, get_condition


class Trait(Condition):
    __obj_name__ = ""

    def __init__(self, X, Y):
        super().__init__(X=X, Y=Y)
        self.is_trait = True


class AmphibiousTrait(Trait):
    __obj_name__ = "ambphibious"

    def init(self):
        self.breath_trait = get_condition('breath_underwater')

    def at_condition(self, caller):

        caller.conditions.add(self.breath_trait)

    def after_condition(self, caller):
        caller.conditions.remove(self.breath_trait)


class BoundTrait(Trait):
    __obj_name__ = "bound"

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
    __obj_name__ = "crawling"

    def at_condition(self, caller):
        cur_max_speed = caller.attrs.speed.max
        # halve current max speed
        self.meta['speed_mod'] = -(cur_max_speed // 2 + 1)
        caller.attrs.speed.add_mod(self.meta['speed_mod'])

    def after_condition(self, caller):
        caller.attrs.modifier['speed'].remove(self.meta['speed_mod'])
        caller.attrs.speed.remove_mod(self.meta['speed_mod'])


class DiseaseResistTrait(Trait):
    __obj_name__ = "disease_resistance"

    def at_condition(self, caller):
        if self.X is None:
            raise ValueError("disease resistance trait must have X defined")


class DiseasedTrait(Trait):
    __obj_name__ = "diseased"

    def at_condition(self, caller):
        if self.X is None:
            raise ValueError("diseased trait must have X defined")


class FlyerTrait(Flying, Trait):
    pass


class FromBeyondTrait(Trait):
    __obj_name__ = "from_beyond"

    def at_condition(self, caller):
        caller.attrs.immunity.value['disease'].append('all')
        caller.attrs.immunity.value['poison'].append('all')
        caller.attrs.immunity.value['condition'].append(Fear)

    def after_condition(self, caller):
        caller.attrs.immunity.value['disease'].remove('all')
        caller.attrs.immunity.value['poison'].remove('all')
        caller.attrs.immunity.value['condition'].remove(Fear)


class ImmunityTrait(Trait):

    __obj_name__ = "immunity"

    def init(self):
        """
        ex:
        mytrait = Immunity(X={'disease': RockJoint})
        """
        self.multi_allow = True
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

        if self.imm_obj != 'all':
            if not inherits_from(self.imm_obj, obj_class_type):
                raise ValueError(
                    "X must be a valid condition, disease, or poison")

    def at_condition(self, caller):
        caller.attrs.immunity.value[self.imm_type].append(self.imm_obj)

    def after_condition(self, caller):
        caller.attrs.immunity.value[self.imm_type].remove(self.imm_obj)


class IncorporealTrait(Trait):
    __obj_name__ = "incorporeal"

    def init(self):
        self.intangile_trait = get_condition('intangible')
        self.flying_trait = get_condition('flying')

    def at_condition(self, caller):

        caller.conditions.add(self.intangile_trait, self.flying_trait)

    def after_condition(self, caller):
        caller.conditions.remove(self.intangile_trait, self.flying_trait)


class NaturalToughnessTrait(Trait):
    __obj_name__ = "natural_toughness"

    def init(self):
        if not self.X or not isinstance(self.X, (int, float)):
            raise ValueError('X must be a valid castable int type')

        self.X = int(self.X)


class NaturalWeaponsTrait(Trait):
    """
    character has unique weapons of some kind;
    ex. claws, teeth, etc... adds , TBD, when fighting
    """
    __obj_name__ = "natural_weapons"

    def init(self):
        if not self.X:
            raise ValueError(
                "natural weapons traits needs a name when initialized")
        self.X = str(self.X)


class PowerWellTrait(Trait):
    __obj_name__ = 'power_well'

    def init(self):
        self.allow_multi = True
        if not self.X or not isinstance(self.X, (int, float)):
            raise ValueError('X must be valid castable int type')

    def at_condition(self, caller):
        # increase max magicka by X
        caller.attrs.magicka.add_mod(self.X)

    def after_condition(self, caller):
        caller.attrs.magicka.remove_mod(self.X)

    def on_duplicate(self, other):
        super().on_duplicate(other)
        new_x = self.X + other.X
        return self.__class__(X=new_x, Y=None)


class SkeletalTrait(Trait):
    __obj_name__ = 'skeletal'

    def init(self):
        self.undead_trait = get_trait('undead')

    def at_condition(self, caller):
        # gain undead trait automatically
        caller.attrs.traits.add(self.undead_trait)
        # immune to burning condition
        caller.attrs.immunity.value['conditions'].append(Burning)

    def after_condition(self, caller):
        caller.attrs.immunity.value['conditions'].remove(Burning)
        caller.attrs.traits.remove(self.undead_trait)


class SilverScarredTrait(Trait):
    __obj_name__ = 'silver_scarred'

    def init(self):
        if not self.X or not isinstance(self.X, (float, int)):
            raise ValueError('silver scarred trait requires damage modifier')

        self.X = float(self.X)


class SpellAbsorptionTrait(Trait):
    __obj_name__ = 'spell_absorption'

    def init(self):
        if not self.X or not isinstance(self.X, (float, int)):
            raise ValueError('spell absorption requires castable int type')

        self.X = int(self.X)
        if self.X > 10:
            self.X = 10


class StuntedMagickaTrait(Trait):
    __obj_name__ = "stunted_magicka"

    def at_condition(self, caller):
        caller.attrs.magicka.rate = 0.0

    def after_condition(self, caller):
        caller.attrs.magicka.rate = 1.0


class SummonedTrait(Trait):
    __obj_name__ = 'summoned'


class SunScarredTrait(Trait):
    __obj_name__ = 'sun_scarred'

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
    __obj_name__ = 'regeneration'

    def init(self):
        if not self.X or not isinstance(self.X, (int, float)):
            raise ValueError('regeneration trait requires castable float type')

        self.X = int(self.X)

    def effect(self, caller, **kwargs):
        """ use to heal player X amnt """
        caller.attrs.change_vital('health', 1)


class ResistanceTrait(Trait):
    __obj_name__ = 'resistance'

    # TODO: add resistant types to this trait (resistant types have not been created or defined yet)
    def init(self):
        self.allow_multi = True
        if not self.X or not isinstance(self.X, (int, float)):
            raise ValueError('resistance trait requires castable float type')

        self.X = float(self.X)


class RunningOutOfLuckTrait(Trait):
    __obj_name__ = 'running_out_of_luck'

    def init(self):
        self.allow_multi = False


class UndeadTrait(Trait):
    __obj_name__ = 'undead'

    def at_condition(self, caller):
        # immune to disease, poison, aging, fatigue
        # dazed, defened
        caller.attrs.immunity.value['disease'].append('all')
        caller.attrs.immunity.value['poison'].append('all')

    def after_condition(self, caller):
        caller.attrs.immunity.value['disease'].append('all')


class UndyingTrait(Trait):
    __obj_name__ = 'undying'

    def at_condition(self, caller):
        # immune to all disease
        caller.attrs.immunity.value['disease'].append('all')

    def after_condition(self, caller):
        caller.attrs.immunity.value['disease'].append('all')


class UnnaturalSensesTrait(Trait):
    __obj_name__ = 'unatural_senses'


class WeaknessTrait(Trait):
    __obj_name__ = 'weakness'

    # TODO: add weakness types to this trait (damage types have not been created or defined yet)

    def init(self):
        if not self.X or not isinstance(self.X, (int, float)):
            raise ValueError("weakness trait requires castable float type")

        self.X = float(self.X)


class TerrifyingTrait(Trait):
    __obj_name__ = 'terrifying'


class ToughTrait(Trait):
    __obj_name__ = 'tough'


class DarkSightTrait(DarkSight, Trait):
    pass


class ResilientTrait(Trait):
    __obj_name__ = 'resilient'

    def init(self):
        if not self.X or not isinstance(self.X, (float, int)):
            raise ValueError('resilient trait requires a castable int type')
        self.X = int(self.X)

    def at_condition(self, caller):
        caller.attrs.health.max += self.X

    def after_condition(self, caller):
        caller.attrs.health.max -= self.X


ALL_TRAITS = [
    AmphibiousTrait,
    BoundTrait,
    CrawlingTrait,
    DarkSightTrait,
    DiseasedTrait,
    DiseaseResistTrait,
    FlyerTrait,
    FromBeyondTrait,
    ImmunityTrait,
    IncorporealTrait,
    NaturalToughnessTrait,
    NaturalWeaponsTrait,
    PowerWellTrait,
    SkeletalTrait,
    SilverScarredTrait,
    SpellAbsorptionTrait,
    StuntedMagickaTrait,
    SummonedTrait,
    SunScarredTrait,
    RegenerationTrait,
    ResilientTrait,
    ResistanceTrait,
    RunningOutOfLuckTrait,
    TerrifyingTrait,
    ToughTrait,
    UndeadTrait,
    UndyingTrait,
    UnnaturalSensesTrait,
    WeaknessTrait,
]


def get_trait(trait_name, x=None, y=None):
    for t in ALL_TRAITS:
        if t.__obj_name__ == trait_name:
            return (t, x, y)
    return None


class RacialTrait(Trait):
    def __str__(self):
        msg = f"{self.name.replace('_', ' ').capitalize()} (|Mracial|g)"
        return msg

    def init(self):
        # do not change this, racial traits aren't meant to have more than once
        self.allow_multi = False


class MentalStrengthRacial(RacialTrait):
    __obj_name__ = "mental_strength"


class InscrutableRacial(RacialTrait):
    __obj_name__ = "inscrutable"


class NaturalArchersRacial(RacialTrait):
    __obj_name__ = "natural_archers"