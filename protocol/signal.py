from .composite import Composite
from .argument import Argument, TypeArgument

class Signal(Composite):
    def __init__(self, adapter, info):
        Composite.__init__(self, adapter)
        self.info = info

    def load(self):
        for x in self.adapter.functionParameters(self.info):
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
