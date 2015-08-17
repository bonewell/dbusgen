from terms.Interface import Interface
from terms.Function import Function
from terms.Structure import Structure
from terms.Parameter import Parameter
from terms.Enumeration import Enumeration
from terms.EnumerationElement import EnumerationElement

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

    def parameters(self, parent):
        """ parent is Structure or Function"""
        pass

    def enumerations(self, interface):
        pass

    def enumeration(self, name, interface):
        pass
