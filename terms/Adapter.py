from terms.Interface import *
from terms.Function import *
from terms.Structure import *
from terms.Enumeration import *
from terms.Parameter import *

class Adapter(object):

    def interfaces(self):
        pass

    def interface(self, name):
        pass

    def functions(self, interface):
        pass

    def function(self, name, interface):
        pass

    def sturctures(self, interface):
        pass

    def structure(self, name, interface):
        pass

    def parameters(self, function):
        pass

    def parameters(self, structure):
        pass

    def enumerations(self, interface):
        pass

    def enumeration(self, name, interface):
        pass
