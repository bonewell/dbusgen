from protocol.Component import Component

class Composite(Component):
    def __init__(self, adapter):
        Component.__init__(self, adapter)
        self.elements = []

    def load(self):
        pass

    def process(self, v):
        if not self.elements:
            self.load()
        for x in self.elements:
            x.accept(v)
