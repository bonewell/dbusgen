from protocol.Composite import Composite 
from protocol.Argument import Argument
from protocol.Argument import TypeArgument

class Signal(Composite):
    def __init__(self, adapter, info):
        Composite.__init__(self, adapter)
        self.info = info

    def load(self):
        for x in self.adapter.parameters(self.info):
            self.elements.append(Argument(self.adapter, x, TypeArgument.Undefined))

    def accept(self, v):
        if v.visit(self):
            self.process(v)

    def name(self):
        return self.info.name

    def provider(self):
        return self.info.provider

    def interface(self):
        return self.info.interface.name
