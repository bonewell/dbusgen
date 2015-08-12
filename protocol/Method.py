from protocol.Composite import Composite
from protocol.Argument import Argument
from protocol.Argument import TypeArgument

class Method(Composite):
    def __init__(self, adapter, request, response):
        Composite.__init__(self, adapter)
        self.request = request
        self.response = response

    def load(self):
        for x in self.adapter.parameters(self.request):
            self.elements.append(Argument(self.adapter, x, TypeArgument.Input))

        for x in self.adapter.parameters(self.response):
            self.elements.append(Argument(self.adapter, x, TypeArgument.Output))

    def accept(self, v):
        if v.visit(self):
            self.process(v)
