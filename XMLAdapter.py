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

    def structures(self, interface):
        structs = []
        query = "interface[@name='%s']/struct" % interface.name
        for item in self.tree.findall(query):
            struct = Structure()
            struct.name = item.get('name')
            struct.interface = interface
            structs.append(struct)
        return structs

    def structure(self, name, interface):
        query = "interface[@name='%s']/struct[@name='%s']" % (interface.name, name)
        item = self.tree.find(query)
        if item is None:
            return None
        struct = Structure()
        struct.name = item.get('name')
        struct.interface = interface
        return struct

    def elements(self, interface, enum):
        els = []
        query = "interface[@name='%s']/enum[@name='%s']/element" % (interface.name, enum.name)
        for item in self.tree.findall(query):
            el = EnumerationElement()
            el.name = item.get('name')
            el.internal_name = item.get('internal_name')
            value = item.get('value')
            el.value = None if value is None else int(value)
            els.append(el)
        return els

    def enumerations(self, interface):
        enums = []
        query = "interface[@name='%s']/enum" % interface.name
        for item in self.tree.findall(query):
            enum = Enumeration()
            enum.name = item.get('name')
            enum.interface = interface
            enum.elements = self.elements(interface, enum)
            enums.append(enum)
        return enums

    def enumeration(self, name, interface):
        query = "interface[@name='%s']/enum[@name='%s']" % (interface.name, name)
        item = self.tree.find(query)
        if item is None:
            return None
        enum = Enumeration()
        enum.name = item.get('name')
        enum.interface = interface
        enum.elements = self.elements(interface, enum)
        return enum
