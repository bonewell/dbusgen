from protocol.Composite import Composite 
from protocol.Enumeration import Enumeration
from protocol.Structure import Structure
from protocol.Signal import Signal
from protocol.Method import Method

class Interface(Composite):
    def __init__(self, adapter, info):
        Composite.__init__(self, adapter)
        self.info = info

    def load(self):
        print('Interface: load')
        for x in self.adapter.enumerations(self.info):
            self.elements.append(Enumeration(x))
        
        for x in self.adapter.structures(self.info):
            self.elements.append(Structure(self.adapter, x))
        
        requests = []
        responses = {}
        for x in self.adapter.functions(self.info):
            if x.type == 'notification':
                self.elements.append(Signal(self.adapter, x))
            if x.type == 'request':
                requests.append(x)
            if x.type == 'response':
                responses[x.name] = x

        for request in requests:
            response = responses[request.name]
            if response is not None:
                self.elements.append(Method(self.adapter, request, response))

    def accept(self, v):
        print('Interface: accept')
        if v.visit(self):
            self.process(v)
