from xml.etree import ElementTree
from protocol.Visitor import Visitor
from protocol.Argument import TypeArgument

class DBusIntrospectionVisitor(Visitor):
    doctype = '<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN" "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">'

    def __init__(self, provider, domain, path):
        self.provider = provider
        self.domain = '%s.%s' % (domain, self.provider)
        self.tree = ElementTree.Element('node', attrib={'name': path})
        self.enums = []
        self.structs = {}

    def visitProtocol(self, host):
        print('Visit protocol')
        return True

    def visitInterface(self, host):
        print('Visit interface %s' % host.info.name)
        name = '%s.%s' % (self.domain, host.info.name)
        self.interface = ElementTree.Element('interface', attrib={'name': name})
        self.empty_interface = True
        return True

    def visitEnumeration(self, host):
        fullname = '%s.%s' % (host.info.interface.name, host.info.name)
        print('Visit enumeration %s' % fullname)
        self.enums.append(fullname)

    def visitStructure(self, host):
        fullname = '%s.%s' % (host.info.interface.name, host.info.name)
        print('Visit structure %s' % fullname)
        self.structs[fullname] = ''
        return True

    def appendInterface(self):
        if self.empty_interface:
            self.tree.append(self.interface)
            self.empty_interface = False

    def visitSignal(self, host):
        print('Visit signal %s' % host.info.name)
        need = host.info.provider == self.provider
        if need:
            self.appendInterface()
            self.parent = ElementTree.Element('signal', attrib={'name': host.info.name})
            self.interface.append(self.parent)
        return need

    def visitMethod(self, host):
        print('Visit method %s' % host.request.name)
        need = host.request.provider == self.provider
        if need:
            self.appendInterface()
            self.parent = ElementTree.Element('method', attrib={'name': host.request.name})
            ElementTree.SubElement(self.parent, 'arg', attrib={'name': 'retCode', 'type': 'i', 'direction': 'out'})
            self.interface.append(self.parent)
        return need

    def prepareStruct(self, host):
        code = self.signature(host)
        fullname = '%s.%s' % (host.info.parent.interface.name, host.info.parent.name)
        self.structs[fullname] += code

    def visitArgument(self, host):
        print('Visit argument %s' % host.info.name)
        if host.info.is_structure:
            self.prepareStruct(host)
        else:
            self.createArgument(host)

    def createArgument(self, host):
        arg = ElementTree.SubElement(self.parent, 'arg', attrib={'name': host.info.name})
        arg.set('type', self.signature(host))
        if host.type == TypeArgument.Input:
            arg.set('direction', 'in')
        if host.type == TypeArgument.Output:
            arg.set('direction', 'out')

    def signature(self, host):
        ptype = host.info.type
        code = ''
        if ptype == 'Integer': code = 'i'
        elif ptype == 'String': code = 's'
        elif ptype == 'Boolean': code = 'b'
        elif ptype == 'Float': code = 'd'
        elif ptype in self.enums: code = 'i'
        elif ptype in self.structs: code = '(%s)' % self.structs[ptype]
        else: raise RuntimeError('Unknown type: %s' % ptype)
        if host.info.is_array: code = 'a%s' % code
        if not host.info.mandatory: code = '(b%s)' % code
        return code

    def xml(self):
        return '%s\n%s' % (self.doctype, ElementTree.tostring(self.tree))
