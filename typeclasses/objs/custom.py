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
    Parent class for book type objects
    """

    __obj_type__ = "book"
    __obj_specific_fields__ = {"author": "", "title": "", "contents": ""}

    def at_object_creation(self):
        """ 
        Construct contents on book based on obj vnum
        which caller sets the key == vnum
        """
        blueprint = GLOBAL_SCRIPTS.objdb.vnum[int(self.key)]


CUSTOM_OBJS = {Default.__obj_type__: Default, Book.__obj_type__: Book}
