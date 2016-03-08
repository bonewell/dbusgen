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

    def restricted(self):
        return self.info.minvalue != None or self.info.maxvalue != None or self.info.minlength > 0 or self.info.maxlength > 0

    def restrictedArray(self):
        return self.isArray() and (self.info.minsize > 0 or self.info.maxsize > 0)

    def minvalue(self):
        try:
            return int(self.info.minvalue)
        except TypeError:
            return None

    def maxvalue(self):
        try:
            return int(self.info.maxvalue)
        except TypeError:
            return None

    def minlength(self):
        try:
            return int(self.info.minlength)
        except TypeError:
            return 0

    def maxlength(self):
        try:
            return int(self.info.maxlength)
        except TypeError:
            return 0

    def minsize(self):
        try:
            return int(self.info.minsize)
        except TypeError:
            return 0

    def maxsize(self):
        try:
            return int(self.info.maxsize)
        except TypeError:
            return 0
