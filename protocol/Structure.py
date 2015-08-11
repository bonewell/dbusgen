from protocol.Composite import Composite
from protocol.Argument import Argument
from protocol.Argument import TypeArgument

class Structure(Composite):
    def __init__(self, adapter, info):
        Composite.__init__(self, adapter)
        self.info = info

    def load(self):
        print('Structure: load')
        for x in self.adapter.parameters(self.info):
            self.elements.append(Argument(x, self.info, TypeArgument.Undefined))

    def accept(self, v):
        print('Structure: accept')
        if v.visit(self):
            self.process(v)
