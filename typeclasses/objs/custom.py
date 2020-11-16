"""
Books that scatter across the world of mundus is filled with rich text and history. This object 
defines what books do and what they contain within.
"""

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
    __obj_specific_fields__ = {'dam_roll': ""}


CUSTOM_OBJS = {
    Default.__obj_type__: Default,
    Book.__obj_type__: Book,
    Weapon.__obj_type__: Weapon
}
