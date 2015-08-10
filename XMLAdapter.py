from xml.etree import ElementTree
from terms.Adapter import *

class XMLAdapter(Adapter):
    def __init__(self, filename):
        self.tree = ElementTree.parse(filename).getroot()

    def data(self):
        """Return content of file"""
        return ElementTree.tostring(self.tree)

    def interfaces(self):
        ifaces = []
        for item in self.tree.findall('interface'):
            iface = Interface()
            iface.name = item.get('name')
            ifaces.append(iface)
        return ifaces

    def interface(self, name):
        item = self.tree.find("interface[@name='%s']" % name)
        if item is None:
            return None
        iface = Interface()
        iface.name = item.get('name')
        return iface

    def functions(self, interface):
        funcs = []
        query = "interface[@name='%s']/function" % interface.name
        for item in self.tree.findall(query):
            func = Function()
            func.name = item.get('name')
            func.type = item.get('messagetype')
            func.provider = item.get('provider')
            func.interface = interface
            funcs.append(func)
        return funcs

    def function(self, name, interface):
        query = "interface[@name='%s']/function[@name='%s']" % (interface.name, name)
        item = self.tree.find(query)
        if item is None:
            return None
        func = Function()
        func.name = item.get('name')
        func.type = item.get('messagetype')
        func.provider = item.get('provider')
        func.interface = interface
        return func

