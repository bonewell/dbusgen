from .composite import Composite
from .interface import Interface

class Protocol(Composite):
    def __init__(self, adapter):
        Composite.__init__(self, adapter)

    def load(self):
        for x in self.adapter.interfaces():
            self.elements.append(Interface(self.adapter, x))

    def accept(self, v):
        if v.visit(self):
            self.process(v)
