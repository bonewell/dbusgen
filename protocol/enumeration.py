from .component import Component

class Enumeration(Component):
    def __init__(self, adapter, info):
        Component.__init__(self, adapter)
        self.info = info

    def accept(self, v):
        v.visit(self)

    def name(self):
        return self.info.name

    def interface(self):
        return self.info.interface.name
