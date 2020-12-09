"""
Things that externally affect the character and their capabilities intead of
features of the characters nature
"""


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
    __obj_name__ = ""
    __activate_msg__ = ""
    __deactivate_msg__ = ""
    __default_x__ = None
    __default_y__ = None

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
        return self.__obj_name__

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
    __obj_name__ = "bleeding"
    __activate_msg__ = "You begin bleeding profusely."
    __deactivate_msg__ = "Your bleeding is under control."
    __default_x__ = 1

    def at_condition(self, caller):
        if self.X is None:
            self.X = self.__default_x__  # default 1

    def effect(self, caller, **kwargs):
        # take damage to caller of value X and end condition
        if self.enabled:
            caller.attrs.health.cur -= self.X
            self.end_condition()


class Blinded(Condition):
    __obj_name__ = "blinded"
    __activate_msg__ = "You can't see a thing!"
    __deactivate_msg__ = "Your sight returns to you."


class Burning(Condition):
    __obj_name__ = 'burning'
    __activate_msg__ = "You are engulfed in flames!"
    __deactivate_msg__ = "The flames around you die down."
    __default_x__ = 1

    def at_condition(self, caller):
        if self.X is None:
            self.X = self.__default_x__

    def effect(self, caller, **kwargs):
        caller.attrs.health.cur -= self.X
        self.X += 1


class Chameleon(Condition):
    __obj_name__ = "chameleon"
    __activate_msg__ = "Your body blends into the background."
    __deactivate_msg__ = "You become more noticeable."


class Crippled(Condition):
    __obj_name__ = "crippled"

    def effect(self, **kwargs):
        # TODO: complicated condition revisit here
        part = kwargs['body_part']


class Dazed(Condition):
    __obj_name__ = 'dazed'
    __activate_msg__ = "Your head begins to spin."
    __deactivate_msg__ = "You regain your concentration."

    def effect(self, caller, **kwargs):
        if self.enabled:
            # reduce action point by 1, minimum of one
            caller.attrs.action_points.value -= 1


class Deafened(Condition):
    __obj_name__ = 'deafened'
    __activate_msg__ = "You lose your hearing!"
    __deactivate_msg__ = "Your hearing comes back."


class DetectInvis(Condition):
    __obj_name__ = 'detect_invis'
    __activate_msg__ = "Your eyes tingle."
    __deactivate_msg__ = "Your eyes go back to normal."


class DetectHidden(Condition):
    __obj_name__ = 'detect_hidden'
    __activate_msg__ = "Your eyes focus."
    __deactivate_msg__ = "Your eyes go back to normal."


class Fatigued(Condition):
    """Fatigued.X refers to level of Fatigue """
    __obj_name__ = 'fatigued'
    __default_x__ = 1

    def at_condition(self, caller):
        if self.X is None:
            self.X = self.__default_x__

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
    __obj_name__ = "frenzied"
    __activate_msg__ = "You enter a state of frenzy."
    __deactivate_msg__ = "You feel yourself again."

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


class HolyLight(Condition):
    __obj_name__ = "holy_light"
    __activate_msg__ = "Your eyes adjust to the true nature of the world."
    __deactivate_msg__ = "You see the world as normal again."


class Hidden(Condition):
    __obj_name__ = 'hidden'
    __activate_msg__ = "You blend into the shadows."


class Immobilized(Condition):
    __obj_name__ = 'immobilized'


class Invisible(Condition):
    __obj_name__ = 'invisible'
    __activate_msg__ = "You fade into the shadows."
    __deactivate_msg__ = "You step out from the shadows."


class Muffled(Condition):
    __obj_name__ = 'muffled'
    __activate_msg__ = "You move more carefully."


class Prone(Condition):
    __obj_name__ = 'prone'
    __activate_msg__ = "You lie down on the ground."
    __deactivate_msg__ = "You get off from the ground."

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
    __obj_name__ = 'paralyzed'
    __activate_msg__ = "You find it impossible to move."
    __deactivate_msg__ = "You regain control in your limbs."


class Restrained(Condition):
    """
    A character is restrained, and thus unable to move, attack or defend themselves.
    Only spells can be cast that do not require motion.
    """
    __obj_name__ = 'restrained'
    __activate_msg__ = "You are restrained."
    __deactivate_msg__ = "You regain control of your body."


class Silenced(Condition):
    __obj_name__ = "silenced"
    __activate_msg__ = "You find it difficult to remember spells."
    __deactivate_msg__ = "The mental block vanishes."

    def at_condition(self, caller):
        self.meta['penalty'] = {'spell': -20}


class Slowed(Condition):
    __obj_name__ = "slowed"
    __activate_msg__ = "You find your body is sluggish to move"

    def at_condition(self, caller):
        cur_speed = caller.attrs.speed.max
        speed_mod = cur_speed // 2 + 1
        caller.attrs.speed.add_mod(-speed_mod)

    def after_condition(self, caller):
        cur_speed = caller.attrs.max_speed
        speed_mod = (cur_speed * 2) - 1
        caller.attrs.speed.remove_mod(-speed_mod)


class Sleeping(Condition):
    __obj_name__ = "sleeping"
    __activate_msg__ = "You fall asleep"
    __deactivate_msg__ = "You wake up"


class Stunned(Condition):
    __obj_name__ = 'stunned'

    def at_condition(self, caller):
        caller.attrs.action_points.value = 0


class Sanctuary(Condition):
    __obj_name__ = "sanctuary"
    __activate_msg__ = "A white aura momentarily surround you"
    __deactivate_msg__ = "Your white aura fades away"

    def at_condition(self, caller):
        pass  # here mutate caller so that damage is halved

    def after_condition(self, caller):
        pass  # remove half damage


class Unconscious(Condition):
    __obj_name__ = 'unconcious'

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
    __obj_name__ = "breath_underwater"
    __activate_msg__ = "Gills grow from your neck"
    __deactivate_msg__ = "Your neck slowly morphs back to normal"


class DarkSight(Condition):
    __obj_name__ = "dark_sight"
    __activate_msg__ = "Your eyes adjust to darkness."
    __deactivate_msg__ = "Your eyes go back to normal."


class Deaf(Condition):
    __obj_name__ = "deaf"


class Fear(Condition):
    __obj_name__ = "fear"


class Intangible(Condition):
    __obj_name__ = 'intangible'


class Flying(Condition):
    __obj_name__ = "flying"
    __activate_msg__ = "You feel lighter than a feather"
    __deactivate_msg__ = "Your feet touch the ground."


class WaterWalking(Condition):
    __obj_name__ = "water_walking"
    __activate_msg__ = "You struggle to sink through water"
    __deactivate_msg__ = "Your weight returns to you."


class Sneak(Condition):
    __obj_name__ = "sneak"
    __activate_msg__ = "You try to move more quietly."


class Diseased(Condition):
    __obj_name__ = "diseased"

    def at_condition(self, caller):
        if self.X is None:
            raise ValueError("diseased trait must have X defined")


ALL_CONDITIONS = {
    Bleeding,
    Blinded,
    Burning,
    BreathUnderWater,
    Chameleon,
    #Crippled,
    DarkSight,
    Dazed,
    Deaf,
    Deafened,
    DetectHidden,
    DetectInvis,
    Diseased,
    Fatigued,
    Fear,
    Flying,
    Frenzied,
    Hidden,
    HolyLight,
    Immobilized,
    Intangible,
    Invisible,
    Muffled,
    Muffled,
    Prone,
    Paralyzed,
    Restrained,
    Sanctuary,
    Silenced,
    Slowed,
    Sleeping,
    Sneak,
    Stunned,
    Unconscious,
    WaterWalking
}


def get_condition(con_name, x=None, y=None):
    for t in ALL_CONDITIONS:
        if t.__obj_name__ == con_name:
            return (t, x, y)
    return None