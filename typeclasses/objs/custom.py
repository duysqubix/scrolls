"""
Books that scatter across the world of mundus is filled with rich text and history. This object 
defines what books do and what they contain within.
"""

from world.globals import WEAR_LOCATIONS
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
    __obj_specific_fields__ = {"author": "", "title": "", "contents": ""}


class Weapon(Object):
    """
    Weapon objects, they deal damagne and can be wielded
    """

    __obj_type__ = "weapon"
    __obj_specific_fields__ = {'dam_roll': "", "dual_wield": "False"}

    def at_object_creation(self):
        super().at_object_creation()
        self.db.wieldable = True  # identifies that obj is equipment type
        self.db.is_wielded = False  # identifies that obj is currently worn


class Equipment(Object):
    """
    Equipable objects
    """
    __obj_type__ = 'equipment'
    __obj_specific_fields__ = {'wear_loc': ""}
    __help_msg__ = f"wear_loc: {', '.join([x.name for x in WEAR_LOCATIONS])}"

    def at_object_creation(self):
        super().at_object_creation()
        self.db.equippable = True  # identifies that obj is equipment type
        self.db.is_worn = False  # identifies that obj is currently worn


CUSTOM_OBJS = {
    Default.__obj_type__: Default,
    Book.__obj_type__: Book,
    Weapon.__obj_type__: Weapon,
    Equipment.__obj_type__: Equipment
}
