from xml.etree import ElementTree
from adapter import Adapter
from terms import *

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
        if item == None:
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

    def function(self, name, interface, type = None):
        if type == None:
            query = "interface[@name='%s']/function[@name='%s']" % (interface.name, name)
        else:
            query = "interface[@name='%s']/function[@name='%s'][@messagetype='%s']" % (interface.name, name, type)
        item = self.tree.find(query)
        if item == None:
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
        if item == None:
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
            el.value = None if value == None else int(value)
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
        if item == None:
            return None
        enum = Enumeration()
        enum.name = item.get('name')
        enum.interface = interface
        enum.elements = self.elements(interface, enum)
        return enum

    def parameters(self, query, parent):
        params = []
        for item in self.tree.findall(query):
            param = self.createParameter(item)
            param.parent = parent
            params.append(param)
        return params

    def functionParameters(self, func):
        query = "interface[@name='%s']/function[@name='%s'][@messagetype='%s']/param" % (func.interface.name, func.name, func.type)
        return self.parameters(query, func)

    def structureParameters(self, struct):
        query = "interface[@name='%s']/struct[@name='%s']/param" % (struct.interface.name, struct.name)
        return self.parameters(query, struct)

    def createParameter(self, item):
        param = Parameter()
        param.name = item.get('name')
        param.type = item.get('type')
        mandatory = item.get('mandatory')
        param.mandatory = False if mandatory == 'false' else True
        minlength = item.get('minlength')
        param.minlength = 0 if minlength == None else minlength
        param.maxlength = item.get('maxlength')
        param.minsize = item.get('minsize')
        param.maxsize = item.get('maxsize')
        is_array = item.get('array')
        param.is_array = True if is_array == 'true' else False
        minvalue = item.get('minvalue')
        param.minvalue = 0 if minvalue == None else minvalue
        param.maxvalue = item.get('maxvalue')
        param.defvalue = item.get('defvalue')
        return param
