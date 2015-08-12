from protocol.Composite import Composite 
from protocol.Argument import Argument
from protocol.Argument import TypeArgument

class Signal(Composite):
    def __init__(self, adapter, info):
        Composite.__init__(self, adapter)
        self.info = info

    def load(self):
        for x in self.adapter.parameters(self.info):
            self.elements.append(Argument(x, TypeArgument.Undefined))

    def accept(self, v):
        if v.visit(self):
            self.process(v)
