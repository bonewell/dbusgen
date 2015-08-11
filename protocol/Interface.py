from protocol.Component import *
from protocol.Composite import *
from protocol.Visitor import *
from terms.Interface import *

class Interface (Component, Composite):

    def load(self):
        for x in adapter.enumerations(info):
          elements.append(Enumeration(x))
        
        for x in adapter.structures(info):
          elements.append(Structure(x))
        
        requests = []
        responses = {}
        for x in adapter.functions(info.name):
          if x.type == 'notification':
            elements.append(Signal(x))
          if x.type == 'request':
            requests.append(x)
          if x.type == 'response':
            responses[x.name] = x
        
        for x in requests:
          y = responses[x.name]
          if y:
            elements.append(Method(x, y))


    def accept(self, v):
        if v.visit(self):
          process(v)




