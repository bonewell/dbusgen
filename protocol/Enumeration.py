from protocol.Component import *
from protocol.Visitor import *
from terms.Enumeration import *

class Enumeration (Component):

    def accept(self, v):
        v.visit(self)




