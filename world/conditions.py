"""
Things that externally affect the character and their capabilities intead of
features of the characters nature
"""
from collections import namedtuple
from evennia.utils import dedent, lazy_property
import evennia


class Condition:
    """
    Base class for condition and traits.
    Traits and conditions are seperate for asthetics, but in 
    a programming sense they are exactly the same thing.

    Args:
        X: generic arg, depending on trait/condition
        Y: generic arg, depending on trait/condition
        enabled: allows effect() method to execute successfully
        allow_multi: determines if more than one of this condition can stack
        copies: keeps track of copies if stacking

    Methods:
        at_condition(self, caller)
            when the condition is first applied to character, this will execute
        
        end_condition(self, caller)
            this will attempt to end the condition, must return bool

        after_condition(self, caller)
            this is called right before condition is actually removed,
            but has passed all the checks to be removed
        
        effect(self, caller)
            function that can be called at will as long as condition/trait is enabled

        on_duplicate(self, other)
            handles logic for if and when a trait/condition is flagged for multi_allow. 
            In backend, traits are stored in 'key:value' pairs, therefore we can't have 
            more than one of the same trait, so this function handles what to do when a 
            duplicate is attempting to join the list of traits.

            The best way to duplicate this is by doing:

            def on_duplicate(self, other):
                super().on_duplicate(other)
                # your code here.
    """
    __conditionname__ = ""
    __msg__ = ""

    def __init__(self, X=None, Y=None):
        self.meta = dict()
        self.X = X
        self.Y = Y
        self.enabled = True
        self.allow_multi = False
        self.init()

    def init(self):
        pass

    @property
    def name(self):
        return self.__conditionname__

    def __str__(self):

        if isinstance(self.X, dict):
            x = f"[{list(self.X.keys())[0]}]"
            y = f"[{list(self.X.values())[0]}]"
        else:
            x = f"[{str(self.X)}]" if self.X is not None else ""
            y = f"[{str(self.Y)}]" if self.Y is not None else ""

        msg = f"{self.name.replace('_', ' ').capitalize()} {x} {y}"
        return msg

    def __repr__(self):
        return f"<{self.name.capitalize()}/{self.X}/{self.Y}>"

    def __eq__(self, other):
        if self.name == other.name and self.X == other.X and self.Y == other.Y and self.allow_multi == other.allow_multi:
            return True
        return False

    def at_condition(self, caller):
        """ things to do when immediately affected by condition"""
        return None

    def effect(self, caller, **kwargs):
        """does the effect of the conditions"""
        return None

    def end_condition(self, caller) -> bool:
        """ to end condition, call this function instead"""
        self.enabled = False
        return True

    def after_condition(self, caller):
        """ things to do when condition ends """
        return None

    def on_duplicate(self, other):
        if not self.multi_allow:
            return None


class Bleeding(Condition):
    __conditionname__ = "bleeding"

    def at_condition(self):
        if self.X is None:
            raise ValueError("bleeding condition must have X defined")

    def effect(self, caller, **kwargs):
        # take damage to caller of value X and end condition
        if self.enabled:
            caller.attrs.health.cur -= self.X
            self.end_condition()


class Blinded(Condition):
    __conditionname__ = "blinded"


class Burning(Condition):
    __conditionname__ = 'burning'

    def effect(self, caller, **kwargs):
        caller.attrs.health.cur -= self.X
        self.X += 1


class Chameleon(Condition):
    __conditionname__ = "chameleon"


class Crippled(Condition):
    __conditionname__ = "crippled"

    def effect(self, **kwargs):
        # TODO: complicated condition revisit here
        part = kwargs['body_part']


class Dazed(Condition):
    __conditionname__ = 'dazed'

    def effect(self, caller, **kwargs):
        if self.enabled:
            # reduce action point by 1, minimum of one
            caller.attrs.action_points.value -= 1


class Deafened(Condition):
    __conditionname__ = 'deafened'


class Fatigued(Condition):
    """Fatigued.X refers to level of Fatigue """
    __conditionname__ = 'fatigued'

    def effect(self, caller, **kwargs):
        if self.enabled:
            if self.X >= 5:  # character dies
                caller.attrs.health.cur = -1
            elif self.X == 4:  # character falls unconcious
                caller.attrs.health.cur = 0
            elif self.X == 3:  # -30 penalty
                self.meta['penalty'] = {'all': -30}
            elif self.X == 2:  # -20
                self.meta['penalty'] = {'all': -20}
            elif self.X == 1:  # -10
                self.meta['penalty'] = {'all': -10}


class Frenzied(Condition):
    __conditionname__ = "frenzied"

    def at_condition(self, caller):
        self.meta['penalty'] = {
            'stats': {
                'prs': -20,
                'prc': -20,
                'wp': -20,
                'int': -20,
                'lck': -20
            }
        }

        self.meta['immunity'] = ['stunned', 'fear', {'wound': 'passive'}]
        caller.stats.str.bonus += 1
        caller.stats.end.bonus += 1

    def after_condition(self, caller):
        caller.stats.str.bonus -= 1
        caller.stats.end.bonus -= 1


class Hidden(Condition):
    __conditionname__ = 'hidden'


class Immobilized(Condition):
    __conditionname__ = 'immobilized'


class Hidden(Condition):
    __conditionname__ = 'invisible'


class Muffled(Condition):
    __conditionname__ = 'muffled'


class Prone(Condition):
    __conditionname__ = 'prone'

    def at_condition(self):
        self.meta['penalty'] = {'fight': -20}

    def end_condition(self, caller):
        if not self.enabled:
            return True

        cost = caller.attrs.speed.max // 2
        cur_speed = caller.attrs.speed.cur
        if (cur_speed - cost) < 0:
            self.enabled = True
            caller.msg("you are too tired to get up")
            return False

        caller.attrs.speed.cur -= cost
        self.enabled = False
        return True


class Paralyzed(Condition):
    """
    A character is frozen, unable to move any poart of their body.
    They may only cast spells that do not require speech or motion
    """
    __conditionname__ = 'paralyzed'


class Restrained(Condition):
    """
    A character is restrained, and thus unable to move, attach or defend themselves.
    Only spells can be cast that do not require motion.
    """
    __conditionname__ = 'restrained'


class Silenced(Condition):
    def at_condition(self, caller):
        self.meta['penalty'] = {'spell': -20}


class Slowed(Condition):
    def at_condition(self, caller):
        cur_speed = caller.attrs.speed.max
        speed_mod = cur_speed // 2 + 1
        caller.attrs.speed.add_mod(-speed_mod)

    def after_condition(self, caller):
        cur_speed = caller.attrs.max_speed
        speed_mod = (cur_speed * 2) - 1
        caller.attrs.speed.remove_mod(-speed_mod)


class Sleeping(Condition):
    __conditionname__ = "sleeping"


class Stunned(Condition):
    __conditionname__ = 'stunned'

    def at_condition(self, caller):
        caller.attrs.action_points.value = 0


class Unconscious(Condition):
    __conditionname__ = 'unconcious'

    def at_condition(self, caller):
        # add prone condition
        caller.conditions.add(Prone)

    def effect(self, caller, **kwargs):
        # check to see if caller has SP 0, if so, they automatically
        # gain X=5 fatigue condition, which utlimately leads to death
        if self.enabled and caller.conditions.has(Fatigued):
            # increase level by one
            fatigued = caller.conditions.get(Fatigued)
            fatigued.X = 5  # kill them....
            caller.conditions.set(fatigued)

    def after_condition(self, caller):
        if self.enabled and caller.conditions.has(Prone):
            caller.conditions.remove(Prone)


class BreathUnderWater(Condition):
    __conditionname__ = "breath_underwater"


class DarkSight(Condition):
    __conditionname__ = "dark_sight"


class Deaf(Condition):
    __conditionname__ = "deaf"


class Fear(Condition):
    __conditionname__ = "fear"


class Intangible(Condition):
    __conditionname__ = 'intangible'


class Flying(Condition):
    __conditionname__ = "flying"


ALL_CONDITIONS = [
    Bleeding, Blinded, Burning, Chameleon, Crippled, DarkSight, Dazed,
    Deafened, Fatigued, Frenzied, Hidden, Muffled, Prone, Paralyzed,
    Restrained, Silenced, Slowed, Sleeping, Stunned, Unconscious,
    BreathUnderWater, Deaf, Fear, Intangible, Flying
]


def get_condition(con_name, x=None, y=None):
    for t in ALL_CONDITIONS:
        if t.__conditionname__ == con_name:
            return (t, x, y)
    return None