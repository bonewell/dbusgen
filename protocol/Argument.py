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

    def accept(self, v):
        print('Argument: accept')
        v.visit(self)
