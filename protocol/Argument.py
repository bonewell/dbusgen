from protocol.Component import *
from terms.Adapter import *
from protocol.Visitor import *
from TypeArgument import *
from terms.Parameter import *

class Argument (Component):

    def accept(self, v):
        v.visit(self)




