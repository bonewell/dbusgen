from protocol.Component import Component

class TypeArgument:
    Undefined = 0
    Input = 1
    Output = 2

class Argument(Component):
    def __init__(self, adapter, info, type = TypeArgument.Undefined):
        Component.__init__(self, adapter)
        self.type = type
        self.info = info
        if not self.is_basic(self.info.type):
            self.info.type = self.fulltype(self.info.type)

    def accept(self, v):
        v.visit(self)

    def fulltype(self, ptype):
        names = ptype.split('.')
        if len(names) > 2:
            raise RuntimeError('Wrong type format: %s' % ptype)
        elif len(names) > 1:
            return ptype
        else:
            fullname = '%s.%s' % (self.info.parent.interface.name, names[0])
            print(fullname)
            return fullname

    def is_basic(self, ptype):
        return ptype in ['Integer', 'String', 'Boolean', 'Float']
