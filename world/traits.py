class Trait:
    __traitname__ = ""

    def __init__(self, X, **kwargs):
        self.X = X
        self.enabled = False

    def enable(self, caller):
        pass

    def disable(self, caller):
        pass


class Amphibious(Trait):
    __traitname__ = "ambphibious"
