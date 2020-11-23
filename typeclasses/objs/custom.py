"""
Books that scatter across the world of mundus is filled with rich text and history. This object 
defines what books do and what they contain within.
"""

from evennia.utils.utils import wrap
from world.globals import DAM_TYPES, WEAR_LOCATIONS
from evennia import GLOBAL_SCRIPTS
from typeclasses.objs.object import Object


class Default(Object):
    __obj_type__ = "default"


class Book(Object):
    """
    Book objects, the core object of the game revolving
    around books
    """

    __obj_type__ = "book"
    __obj_specific_fields__ = {
        "category": "",
        "date": "",
        "author": "",
        "title": "",
        "contents": ""
    }


class Container(Object):
    """
    Object that can hold things
    """
    __obj_type__ = 'container'
    __obj_specific_fields__ = {'limit': -1}
    __help_msg__ = ["limit: [int] - number of objects, -1 for infinity"]


class Weapon(Object):
    """
    Weapon objects, they deal damage and can be wielded
    """

    __obj_type__ = "weapon"
    __obj_specific_fields__ = {"dam_type": "", 'dam_roll': ""}
    __help_msg__ = [
        f"dam_type:{wrap(' '.join(DAM_TYPES['physical']))}",
        "dam_roll: ex: 1d10+4"
    ]

    def at_object_creation(self):
        super().at_object_creation()
        self.db.wieldable = True  # identifies that obj is equipment type
        self.db.is_wielded = False  # identifies that obj is currently worn


class Staff(Weapon):
    """
    Staff objects, like weapons that deal only magical
    damage, have limited charges, and are recharged by soul gems
    """
    __obj_type__ = "staff"
    __obj_specific_fields__ = {"dam_type": "", 'dam_roll': "", "charges": -1}
    __help_msg__ = [
        f"dam_type: {wrap(', '.join(DAM_TYPES['magical']))}",
        "dam_roll: ex: 1d10+4",
        "charges: [int] - number of charges, -1 for infinity"
    ]


class Equipment(Object):
    """
    Equipable objects
    """
    __obj_type__ = 'equipment'
    __obj_specific_fields__ = {'wear_loc': ""}
    __help_msg__ = [f"wear_loc: {', '.join([x.name for x in WEAR_LOCATIONS])}"]

    def at_object_creation(self):
        super().at_object_creation()
        self.db.equippable = True  # identifies that obj is equipment type
        self.db.is_worn = False  # identifies that obj is currently worn


CUSTOM_OBJS = {
    Book.__obj_type__: Book,
    Container.__obj_type__: Container,
    Default.__obj_type__: Default,
    Equipment.__obj_type__: Equipment,
    Staff.__obj_type__: Staff,
    Weapon.__obj_type__: Weapon,
}
