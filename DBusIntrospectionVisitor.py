from xml.etree import ElementTree
from protocol.Visitor import Visitor
from protocol.Argument import TypeArgument

class DBusIntrospectionVisitor(Visitor):
    doctype = '<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN" "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">'

    def __init__(self, provider, domain, path):
        self.provider = provider
        self.domain = domain
        self.tree = ElementTree.Element('node', attrib={'name': path})
        self.enums = []
        self.structs = {}

    def visitProtocol(self, protocol):
        print('Visit protocol')
        return True

    def visitInterface(self, iface):
        print('Visit interface %s' % iface.name())
        name = '%s.%s.%s' % (self.domain, self.provider, iface.name())
        self.iface = ElementTree.Element('interface', attrib={'name': name})
        self.empty_iface = True
        return True

    def visitEnumeration(self, enum):
        fullname = '%s.%s' % (enum.interface(), enum.name())
        print('Visit enumeration %s' % fullname)
        self.enums.append(fullname)

    def visitStructure(self, struct):
        fullname = '%s.%s' % (struct.interface(), struct.name())
        print('Visit structure %s' % fullname)
        self.structs[fullname] = ''
        return True

    def appendInterface(self):
        if self.empty_iface:
            self.tree.append(self.iface)
            self.empty_iface = False

    def visitSignal(self, signal):
        print('Visit signal %s' % signal.name())
        need = signal.provider() == self.provider
        if need:
            self.appendInterface()
            self.parent = ElementTree.Element('signal', attrib={'name': signal.name()})
            self.iface.append(self.parent)
        return need

    def visitMethod(self, method):
        print('Visit method %s' % method.name())
        need = method.provider() == self.provider
        if need:
            self.appendInterface()
            self.parent = ElementTree.Element('method', attrib={'name': method.name()})
            el = ElementTree.Element('arg', attrib={'name': 'retCode', 'type': 'i', 'direction': 'out'})
            self.parent.append(el)
            self.iface.append(self.parent)
        return need

    def prepareStruct(self, struct):
        code = self.signature(struct)
        fullname = '%s.%s' % (struct.interface(), struct.parent())
        self.structs[fullname] += code

    def visitArgument(self, arg):
        print('Visit argument %s' % arg.name())
        if arg.isStruct():
            self.prepareStruct(arg)
        else:
            self.createArgument(arg)

    def createArgument(self, arg):
        el = ElementTree.Element('arg', attrib={'name': arg.name()})
        el.set('type', self.signature(arg))
        if arg.direction == TypeArgument.Input:
            el.set('direction', 'in')
        if arg.direction == TypeArgument.Output:
            el.set('direction', 'out')
        self.parent.append(el)

    def signature(self, arg):
        if arg.type() == 'Integer': code = 'i'
        elif arg.type() == 'String': code = 's'
        elif arg.type() == 'Boolean': code = 'b'
        elif arg.type() == 'Float': code = 'd'
        elif arg.type() in self.enums: code = 'i'
        elif arg.type() in self.structs: code = '(%s)' % self.structs[arg.type()]
        else: raise RuntimeError('Unknown type: %s' % arg.type())
        if arg.isArray(): code = 'a%s' % code
        if not arg.isMandatory(): code = '(b%s)' % code
        return code

    def xml(self, interface = None):
        tree = self.tree
        if interface is not None:
            fullname = '%s.%s.%s' % (self.domain, self.provider, interface)
            tree = self.tree.find("interface[@name='%s']" % fullname)
            if tree is None:
                raise RuntimeError('Unknown interface: %s' % interface)
        return '%s\n%s' % (self.doctype, ElementTree.tostring(tree))
