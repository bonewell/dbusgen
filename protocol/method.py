from .composite import Composite
from .argument import Argument, TypeArgument

class Method(Composite):
    def __init__(self, adapter, request, response):
        Composite.__init__(self, adapter)
        self.request = request
        self.response = response

    def load(self):
        for x in self.adapter.functionParameters(self.request):
            self.elements.append(Argument(self.adapter, x, TypeArgument.Input))

        for x in self.adapter.functionParameters(self.response):
            self.elements.append(Argument(self.adapter, x, TypeArgument.Output))

    def accept(self, v):
        if v.visit(self):
            self.process(v)

    def name(self):
        return self.request.name

    def provider(self):
        return self.request.provider

    def interface(self):
        return self.request.interface.name
