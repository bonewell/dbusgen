from protocol.Composite import Composite
from protocol.Interface import Interface

class Protocol(Composite):
    def __init__(self, adapter):
        Composite.__init__(self, adapter)

    def load(self):
        print('Protocol: load')
        for x in self.adapter.interfaces():
            self.elements.append(Interface(self.adapter, x))

    def accept(self, v):
        print('Protocol: accept')
        if v.visit(self):
            self.process(v)
