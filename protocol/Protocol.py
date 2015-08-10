from protocol.Component import *
from protocol.Composite import *
from protocol.Visitor import *

class Protocol (Component, Composite):

    def load(self):
        for x in adapter.interfaces():
          elements.append(Interface(x))


    def accept(self, v):
        if v.visit(self):
          process(v)




