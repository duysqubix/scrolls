"""
Things that externally affect the character and their capabilities intead of
features of the characters nature
"""
from evennia.utils import dedent, lazy_property
import evennia


class Condition:
    __conditionname__ = ""
    __msg__ = ""

    def __init__(self, X=None):
        self.meta = dict()
        self.X = X
        self.enabled = True
        self.multiple = False
        self.init()

    def init(self):
        pass

    @property
    def name(self):
        return self.__conditionname__

    def __str__(self):
        msg = f"""
            {self.name}: {self.meta}   
        """
        return dedent(msg)

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
    __conditionname__ = "breath underwater"


class DarkSight(Condition):
    __conditionname__ = "dark sight"


class Deaf(Condition):
    __conditionname__ = "deaf"


class Fear(Condition):
    __conditionname__ = "fear"


class Intangible(Condition):
    __conditionname__ = 'intangible'


class Flying(Condition):
    __conditionname__ = "flying"