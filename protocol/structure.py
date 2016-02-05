from .composite import Composite
from .argument import Argument, TypeArgument

class Structure(Composite):
    structures = {}

    def __init__(self, adapter, info):
        Composite.__init__(self, adapter)
        self.info = info
        Structure.structures['.'.join((self.info.name, self.info.interface.name))] = self

    def load(self):
        for x in self.adapter.structureParameters(self.info):
            arg = Argument(self.adapter, x, TypeArgument.Undefined)
            arg.of_structure = True
            arg.is_structure = Structure.exist(arg.type())
            self.elements.append(arg)

    def accept(self, v):
        if v.visit(self):
            self.process(v)

    def name(self):
        return self.info.name

    def interface(self):
        return self.info.interface.name

    @staticmethod
    def exist(name):
        return name in Structure.structures
