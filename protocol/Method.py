from protocol.Component import *
from protocol.Composite import *
from protocol.Argument import *
from terms.Adapter import *
from protocol.Visitor import *
from terms.Function import *

class Method (Component, Composite):

    def load(self):
        for x in adapter.parameters(request):
          elements.append(Argument(x, Input))
        
        for x in adapter.parameters(response):
          elements.append(Argument(x, Output))


    def accept(self, v):
        if v.visit(self):
          process(v)




