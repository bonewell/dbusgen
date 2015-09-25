from .component import Component

class TypeArgument:
    Undefined = 0
    Input = 1
    Output = 2

class Argument(Component):
    def __init__(self, adapter, info, direction = TypeArgument.Undefined):
        Component.__init__(self, adapter)
        self.info = info
        self.direction = direction
        self.of_structure = False
        self.is_structure = False

    def accept(self, v):
        v.visit(self)

    def fulltype(self):
        names = self.info.type.split('.')
        if not self.info.type or len(names) > 2:
            raise RuntimeError('Wrong type format: %s' % self.info.type)
        elif len(names) > 1:
            return self.info.type
        else:
            fullname = '%s.%s' % (self.interface(), names[0])
            return fullname

    def isBasic(self):
        return self.info.type in ('Integer', 'String', 'Boolean', 'Float')

    def name(self):
        return self.info.name

    def type(self):
        if not self.isBasic():
            return self.fulltype()
        return self.info.type

    def interface(self):
        return self.info.parent.interface.name

    def parent(self):
        return self.info.parent.name

    def isStruct(self):
        return self.is_structure

    def isArray(self):
        return self.info.is_array

    def isMandatory(self):
        return self.info.mandatory

    def ofStruct(self):
        return self.of_structure
