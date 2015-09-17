from collections import OrderedDict
from protocol.Visitor import Visitor
from protocol.Argument import TypeArgument

class MessageDescriptionVisitor(Visitor):
    tpl_type_message = "const %s::MessageDescription"
    tpl_type_structure = "const %s::StructDescription"
    tpl_type_array = "const %s::ArrayDescription"
    tpl_type_parameter = "const %s::ParameterDescription"

    tpl_structs = "struct Structs {\n%s};"
    tpl_structs_member = "  static %(type)s* %(name)s__parameters[];\n"

    tpl_definition_structure = "%(type)s* Structs::%(name)s__parameters[] = {\n%(args)s  NULL };"
    tpl_definition_structure_member = "  (%(type)s*)&%(name)s__parameter%(id)d,\n"
    tpl_structure_parameter = "%(type)s %(name)s__parameter%(id)d = {\n%(info)s};\n"
    tpl_parameter_info = '  "%(name)s",\n  %(type)s,\n  %(mandatory)s\n'
    tpl_parameter_array_info = '  {\n    "%(name)s",\n    %(type)s,\n    %(mandatory)s\n  },\n  %(array)s,\n  "%(introspection)s"\n'
    tpl_parameter_structure_info = '  {\n    "%(name)s",\n    %(type)s,\n    %(mandatory)s\n  },\n  Structs::%(struct)s__parameters\n'
    tpl_parameter_array = "%(type)s %(name)s__parameter%(id)d_array = {\n%(info)s};\n"
    tpl_parameter_array_item = "(%(type)s*)&%(name)s__parameter%(id)d_array"

    tpl_messages = "const MessageDescription* message_descriptions[] = {\n%s  NULL\n};"
    tpl_messages_member = "  &%(name)s__%(type)s,\n"

    def __init__(self, namespace):
        self.namespace = namespace
        self.doTypes()
        self.enums = []
        self.names = []
        self.structures = OrderedDict()
        self.signatures = {}
        self.methods = {}
        self.signals = OrderedDict()
        self.args = OrderedDict()
        self.logs = False

    def doTypes(self):
        self.type_message = self.tpl_type_message % self.namespace
        self.type_structure = self.tpl_type_structure % self.namespace
        self.type_array = self.tpl_type_array % self.namespace
        self.type_parameter = self.tpl_type_parameter % self.namespace

    def visitProtocol(self, protocol):
        if self.logs: print('Visit protocol')
        return True

    def visitInterface(self, iface):
        if self.logs: print('Visit interface %s' % iface.name())
        return True

    def visitEnumeration(self, enum):
        fullname = '%s.%s' % (enum.interface(), enum.name())
        if self.logs: print('Visit enumeration %s' % fullname)
        self.enums.append(fullname)

    def visitStructure(self, struct):
        fullname = (struct.interface(), struct.name())
        if self.logs: print('Visit structure %s' % '.'.join(fullname))
        self.names.append(fullname)
        self.structures[(struct.interface(), struct.name())] = []
        self.signatures['.'.join(fullname)] = ''
        return True

    def visitSignal(self, signal):
        fullname = (signal.interface(), signal.name())
        if self.logs: print('Visit signal %s' % '.'.join(fullname))
        self.names.append(fullname)
        self.signals[(signal.interface(), signal.name())] = signal
        self.args[(signal.interface(), signal.name())] = []
        self.index = 1
        return True

    def visitMethod(self, method):
        fullname = (method.interface(), method.name())
        if self.logs: print('Visit method %s' % '.'.join(fullname))
        self.names.append(fullname)
        self.methods[(method.interface(), method.name())] = method
        self.args[(method.interface(), method.name())] = []
        self.index = 1
        return True

    def prepareStruct(self, struct):
        self.structures[(struct.interface(), struct.parent())].append(struct)
        code = self.signature(struct)
        fullname = '%s.%s' % (struct.interface(), struct.parent())
        self.signatures[fullname] += code

    def visitArgument(self, arg):
        if self.logs: print('Visit argument %s' % arg.name())
        if arg.isStruct():
            self.prepareStruct(arg)
        else:
            self.createArgument(arg)

    def createArgument(self, arg):
        self.args[(arg.interface(), arg.parent())].append({'id': self.index, 'arg': arg})
        self.index += 1

    def signature(self, arg, array=False):
        if arg.type() == 'Integer': code = 'i'
        elif arg.type() == 'String': code = 's'
        elif arg.type() == 'Boolean': code = 'b'
        elif arg.type() == 'Float': code = 'd'
        elif arg.type() in self.enums: code = 'i'
        elif arg.type() in self.signatures: code = '(%s)' % self.signatures[arg.type()]
        else: raise RuntimeError('Unknown type: %s' % arg.type())
        if not array and arg.isArray(): code = 'a%s' % code
        if not array and not arg.isMandatory(): code = '(b%s)' % code
        return code

    def fulltype(self, arg, array=False):
        if not array and arg.isArray(): code = 'Array'
        elif arg.type() in self.enums: code = 'Enum'
        elif arg.type() in self.signatures: code = 'Struct'
        else: code = arg.type()
        return '%s::%s' % (self.namespace, code)

    def structs(self):
        return self.tpl_structs % self.structs_members()

    def structs_members(self):
        structs = ''
        for member in self.structures:
            data = {'type': self.type_parameter, 'name': "__".join(member)}
            structs += self.tpl_structs_member % data
        return structs

    def definition(self, name):
        if name in self.structures:
            return self.definition_structure(name)
        elif name in self.signals:
            return self.definition_signal(name)
        elif name in self.methods:
            return self.definition_method(name)
        return ''

    def definition_structure(self, name):
        return self.structure_parameters(name) + self.structure_array_parameters(name)

    def structure_parameters(self, name):
        parameters = ''
        uid = 1
        for arg in self.structures[name]:
            parameters += self.structure_parameter(name, arg, uid)
            uid += 1
        return parameters

    def structure_parameter(self, name, arg, uid):
        desc = ''
        type_parameter = self.type_parameter
        info = self.parameter_info(name, arg, uid)
        if arg.isArray():
           desc += self.parameter_array(name, arg, uid)
           type_parameter = self.type_array
           info = self.parameter_array_info(name, arg, uid)
        elif arg.type() in self.signatures:
           type_parameter = self.type_structure
           info = self.parameter_structure_info(name, arg, uid)
        data = {'type': type_parameter, 'name': "__".join(name), 'id': uid, 'info': info}
        desc += self.tpl_structure_parameter % data
        return desc

    def parameter_info(self, name, arg, uid, mandatory=None):
        mandatory = 'true' if mandatory or arg.isMandatory() else 'false'
        data = {'name': arg.name(), 'type': self.fulltype(arg, True), 'mandatory': mandatory}
        return self.tpl_parameter_info % data

    def parameter_array_info(self, name, arg, uid):
        mandatory = 'true' if arg.isMandatory() else 'false'
        data = {'name': arg.name(), 'type': self.fulltype(arg), 'mandatory': mandatory, 'array': self.parameter_array_item(name, arg, uid), 'introspection': self.signature(arg, True)}
        return self.tpl_parameter_array_info % data

    def parameter_array_item(self, name, arg, uid):
        data = {'type': self.type_parameter, 'name': "__".join(name), 'id': uid}
        return self.tpl_parameter_array_item % data

    def parameter_structure_info(self, name, arg, uid, mandatory=None):
        mandatory = 'true' if mandatory or arg.isMandatory() else 'false'
        data = {'name': arg.name(), 'type': self.fulltype(arg, True), 'mandatory': mandatory, 'struct': arg.type().replace('.', "__")}
        return self.tpl_parameter_structure_info % data

    def parameter_array(self, name, arg, uid):
        type_parameter = self.type_parameter
        info = self.parameter_info(name, arg, uid, True)
        if arg.type() in self.signatures:
            type_parameter = self.type_structure
            info = self.parameter_structure_info(name, arg, uid, True)
        data = {'type': type_parameter, 'name': "__".join(name), 'id': uid, 'info': info}
        return self.tpl_parameter_array % data

    def structure_array_parameters(self, name):
        data = {'type': self.type_parameter, 'name': "__".join(name), 'args': self.structure_members(name)}
        return self.tpl_definition_structure % data

    def structure_members(self, name):
        definition = ''
        uid = 1
        for arg in self.structures[name]:
            definition += self.definition_structure_member(name, uid)
            uid += 1
        return definition

    def definition_structure_member(self, name, uid):
        data = {'type': self.type_parameter, 'name': "__".join(name), 'id': uid}
        return self.tpl_definition_structure_member % data

    def definition_signal(self, name):
        return 'Notification'

    def definition_method(self, name):
        return 'Request, Response'

    def messages(self):
        return self.tpl_messages % self.messages_members()

    def messages_members(self):
        messages = ''
        for member in self.names:
            if member in self.structures:
               continue
            if member in self.signals:
                data = {'type': 'notification', 'name': "__".join(member)}
                messages += self.tpl_messages_member % data
            elif member in self.methods:
                data = {'type': 'request', 'name': "__".join(member)}
                messages += self.tpl_messages_member % data
                data = {'type': 'response', 'name': "__".join(member)}
                messages += self.tpl_messages_member % data
        return messages
