from protocol.Component import *
from protocol.Composite import *
from protocol.Visitor import *
from terms.Structure import *

class Structure (Component, Composite):

    def load(self):
        for x in adapter.parameters(info):
          elements.append(Argument(x, Undefined))


    def accept(self, v):
        if v.visit(self):
          process(v)




