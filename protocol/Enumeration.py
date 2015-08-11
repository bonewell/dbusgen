from protocol.Component import Component

class Enumeration(Component):
    def accept(self, v):
        print('Enumeration: accept')
        v.visit(self)
