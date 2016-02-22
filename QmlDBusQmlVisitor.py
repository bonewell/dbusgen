from collections import OrderedDict
from protocol import Visitor, TypeArgument

class QmlDBusQmlVisitor(Visitor):
    tpl_enumerate = 'var %(name)s = {\n%(items)s\n}\n'

    tpl_element = '  %s: %d'

    tpl_signal = '  signal %(lowername)s(%(params)s)\n  on%(name)s: console.debug("emitted %(interface)s:%(name)s")'

    tpl_method = '''  function %(name)s(params) {
    console.debug("%(interface)sProxy::%(name)s")
    try {
      if("%(name)s" in sdl%(interface)s)
        return sdl%(interface)s.%(name)s(%(params)s)
      else
        return { "__errno": Common.Result.UNSUPPORTED_REQUEST }
    } catch(err) {
        return { "__errno": err }
    }
  }
'''

    def __init__(self, version="5.1.0", logs=False):
        self.variant = 'variant' if version == '4.8.5' else 'var'
        self.enums = OrderedDict()
        self.enums_names = []
        self.names = []
        self.ifaces = []
        self.structures = OrderedDict()
        self.signals_list = OrderedDict()
        self.methods_list = OrderedDict()
        self.args = OrderedDict()
        self.logs = logs

    def visitProtocol(self, protocol):
        if self.logs: print('Visit protocol')
        return True

    def visitInterface(self, iface):
        if self.logs: print('Visit interface %s' % iface.name())
        self.ifaces.append(iface.name())
        self.enums[iface.name()] = []
        self.signals_list[iface.name()] = []
        self.methods_list[iface.name()] = []
        return True

    def visitEnumeration(self, enum):
        fullname = '%s.%s' % (enum.interface(), enum.name())
        if self.logs: print('Visit enumeration %s' % fullname)
        self.enums[enum.interface()].append(enum)
        self.enums_names.append(fullname)
        return True

    def visitStructure(self, struct):
        fullname = (struct.interface(), struct.name())
        if self.logs: print('Visit structure %s' % '.'.join(fullname))
        self.structures[(struct.interface(), struct.name())] = []
        self.names.append('.'.join(fullname))
        return True

    def visitSignal(self, signal):
        fullname = (signal.interface(), signal.name())
        if self.logs: print('Visit signal %s' % '.'.join(fullname))
        if signal.provider() == 'hmi':
            self.signals_list[signal.interface()].append(signal)
            self.args[(signal.interface(), signal.name())] = []
            return True
        else:
            return False

    def visitMethod(self, method):
        fullname = (method.interface(), method.name())
        if self.logs: print('Visit method %s' % '.'.join(fullname))
        if method.provider() == 'hmi':
            self.methods_list[method.interface()].append(method)
            self.args[(method.interface(), method.name())] = []
            return True
        else:
            return False

    def prepareStruct(self, struct):
        self.structures[(struct.interface(), struct.parent())].append(struct)

    def visitArgument(self, arg):
        if self.logs: print('Visit argument %s' % arg.name())
        if arg.ofStruct():
            self.prepareStruct(arg)
        else:
            self.createArgument(arg)

    def createArgument(self, arg):
        self.args[(arg.interface(), arg.parent())].append(arg)

    def qml_param_type(self, arg):
        typename = arg.type()
        if arg.isArray() or arg.isStruct() or not arg.isMandatory(): code = self.variant
        elif typename == 'Integer': code = 'int'
        elif typename == 'String': code = 'string'
        elif typename == 'Boolean': code = 'bool'
        elif typename == 'Float': code = 'double'
        elif typename in self.enums_names: code = 'int' 
        else: code = self.variant
        return code

    def interfaces(self):
        return self.ifaces

    def signals(self, interface):
        return self.signals_list[interface]

    def signal(self, signal):
        lowername = signal.name()[:1].lower() + signal.name()[1:]
        params = self.signal_params(signal)
        return self.tpl_signal % { 'interface': signal.interface(), 'name': signal.name(), 'params': params, 'lowername': lowername}

    def signal_params(self, signal):
        key = (signal.interface(), signal.name())
        return ', '.join([ '%s %s' % (self.qml_param_type(p), p.name()) for p in self.args[key] ])

    def method(self, method):
        name = method.name()[:1].lower() + method.name()[1:]
        return self.tpl_method % { 'interface': method.interface(), 'name': name, 'params': self.method_params(method) }

    def method_params(self, method):
        key = (method.interface(), method.name())
        return ', '.join([ 'params.%s' % p.name() for p in self.args[key] if p.direction == TypeArgument.Input ])

    def methods(self, interface):
        return self.methods_list[interface]

    def enumerates(self, interface):
        return self.enums[interface]

    def enum(self, enum):
        return self.tpl_enumerate % { 'name': enum.name(), 'items': self.enum_values(enum) }

    def enum_values(self, enum):
        self.uid = 0
        return ',\n'.join([ self.element(e) for e in enum.info.elements ])

    def element(self, e):
        name = e.internal_name if e.internal_name else e.name
        value = e.value if e.value else self.uid
        self.uid += 1
        return self.tpl_element % (name, value)
