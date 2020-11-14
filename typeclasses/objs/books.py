"""
Books that scatter across the world of mundus is filled with rich text and history. This object 
defines what books do and what they contain within.
"""

from typeclasses.objects import Object


class Book(Object):
    """
    Parent class for book type objects
    """
    def basetype_setup(self):
        super().basetype_setup()
        self.locks.add(";".join(["call:false()", "puppet:false()"]))

        self.db.key = ""
        self.db.author = ""
        self.db.title = ""
        self.db.contents = ""