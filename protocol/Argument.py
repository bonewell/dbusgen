from protocol.Component import Component

class TypeArgument:
    Undefined = 0
    Input = 1
    Output = 2

class Argument(Component):
    def __init__(self, adapter, info, direction = TypeArgument.Undefined):
        Component.__init__(self, adapter)
        self.info = info
        self.direction = direction
        if not self.isBasic():
            self.info.type = self.fulltype()

    def accept(self, v):
        v.visit(self)

    def fulltype(self):
        names = self.info.type.split('.')
        if len(names) > 2:
            raise RuntimeError('Wrong type format: %s' % self.info.type)
        elif len(names) > 1:
            return self.info.type
        else:
            fullname = '%s.%s' % (self.interface(), names[0])
            print(fullname)
            return fullname

    def isBasic(self):
        return self.info.type in ['Integer', 'String', 'Boolean', 'Float']

    def name(self):
        return self.info.name

    def type(self):
        return self.info.type

    def interface(self):
        return self.info.parent.interface.name

    def parent(self):
        return self.info.parent.name

    def isStruct(self):
        return self.info.is_structure

    def isArray(self):
        return self.info.is_array

    def isMandatory(self):
        return self.info.mandatory
