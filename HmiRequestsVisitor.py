from collections import OrderedDict
from protocol import Visitor, TypeArgument

class HmiRequestsVisitor(Visitor):
    tpl_type_message = "const %s::MessageDescription"
    tpl_type_structure = "const %s::StructDescription"
    tpl_type_array = "const %s::ArrayDescription"
    tpl_type_parameter = "const %s::ParameterDescription"

    tpl_structs = "struct Structs {\n%s};"
    tpl_structs_member = "  static %(type)s* %(name)s__parameters[];\n"

    tpl_definition_structure = "%(type)s* Structs::%(name)s__parameters[] = {\n%(args)s  NULL };"
    tpl_structure_member = "  (%(type)s*)&%(name)s__parameter%(id)d,\n"
    tpl_definition_structure_member = "%(type)s %(name)s__parameter%(id)d = {\n%(info)s};\n"

    tpl_definition_function = "%(type)s* %(name)s__%(kind)s__parameters[] = {\n%(args)s  NULL };\n"
    tpl_function_member = "  (%(type)s*)&%(name)s__%(kind)s__parameter%(id)d,\n"
    tpl_definition_function_member = "%(type)s %(name)s__%(kind)s__parameter%(id)d = {\n%(info)s};\n"

    tpl_parameter_info = '  "%(name)s",\n  %(type)s,\n  %(mandatory)s\n'
    tpl_parameter_array_info = '  {\n    "%(name)s",\n    %(type)s,\n    %(mandatory)s\n  },\n  %(array)s,\n  "%(introspection)s"\n'
    tpl_parameter_structure_info = '  {\n    "%(name)s",\n    %(type)s,\n    %(mandatory)s\n  },\n  Structs::%(struct)s__parameters\n'
    tpl_parameter_array = "%(type)s %(name)s__%(kind)sparameter%(id)d_array = {\n%(info)s};\n"
    tpl_parameter_array_item = "(%(type)s*)&%(name)s__%(kind)sparameter%(id)d_array"

    tpl_messages = "const MessageDescription* message_descriptions[] = {\n%s  NULL\n};"
    tpl_messages_member = "  &%(name)s__%(type)s,\n"
    tpl_definition_message = "%(type)s %(name)s__%(kind)s = {\n%(info)s};"
    tpl_message_info = '  "%(interface)s",\n  "%(nick)s",\n  hmi_apis::messageType::%(kind)s,\n  hmi_apis::FunctionID::%(type)s,\n  %(name)s__%(kind)s__parameters\n'

    def __init__(self):
        self.doTypes()
        self.enums = []
        self.names = []
        self.structures = OrderedDict()
        self.signatures = {}
        self.methods = OrderedDict()
        self.args = OrderedDict()
        self.logs = False

    def doTypes(self):
        self.namespace = ''
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
        return True

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
        return False

    def visitMethod(self, method):
        fullname = (method.interface(), method.name())
        if self.logs: print('Visit method %s' % '.'.join(fullname))
        if method.provider() == 'sdl':
            self.names.append(fullname)
            self.methods[(method.interface(), method.name())] = method
            self.args[(method.interface(), method.name())] = []
            return True
        else:
            return False

    def prepareStruct(self, struct):
        self.structures[(struct.interface(), struct.parent())].append(struct)
        code = self.signature(struct)
        fullname = '%s.%s' % (struct.interface(), struct.parent())
        self.signatures[fullname] += code

    def visitArgument(self, arg):
        if self.logs: print('Visit argument %s' % arg.name())
        if arg.ofStruct():
            self.prepareStruct(arg)
        else:
            self.createArgument(arg)

    def createArgument(self, arg):
        self.args[(arg.interface(), arg.parent())].append(arg)

    def arraySignature(self, arg):
        typename = arg.type()
        if typename == 'Integer': code = 'i'
        elif typename == 'String': code = 's'
        elif typename == 'Boolean': code = 'b'
        elif typename == 'Float': code = 'd'
        elif typename in self.enums: code = 'i'
        elif typename in self.signatures: code = '(%s)' % self.signatures[typename]
        else: raise RuntimeError('Unknown type: %s' % typename)
        return code

    def signature(self, arg):
        code = self.arraySignature(arg)
        if arg.isArray(): code = 'a%s' % code
        if not arg.isMandatory(): code = '(b%s)' % code
        return code

    def arrayType(self, arg):
        code = arg.type()
        if code in ('Integer', 'String', 'Boolean', 'Float'):
            return '%s::%s' % (self.namespace, code)
        if code in self.enums:
            return '%s::Enum' % self.namespace
        if code in self.signatures:
            return '%s::Struct' % self.namespace
        raise RuntimeError('Unknown type: %s' % code)

    def fulltype(self, arg):
        if arg.isArray(): 
           return '%s::Array' % self.namespace
        else:
           return self.arrayType(arg)

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
        raise RuntimeError('Unknown name of data')

    def definition_structure(self, name):
        return (self.structure_members(name, True) +
        self.structure_array_parameters(name))

    def definition_signal(self, name):
        return (self.function_members(name, 'notification', True) +
        self.function_array_parameters(name, 'notification') +
        self.function_info(name, 'notification'))

    def definition_method(self, name):
        return (self.function_members(name, 'request', True) +
        self.function_array_parameters(name, 'request') +
        self.function_info(name, 'request') + '\n\n' +
        self.function_members(name, 'response', True) +
        self.function_array_parameters(name, 'response') +
        self.function_info(name, 'response'))

    def function_info(self, name, kind):
        info = self.function_description(name, kind)
        data = {'type': self.type_message, 'name': "__".join(name),
        'kind': kind, 'info': info}
        return self.tpl_definition_message % data

    def function_description(self, name, kind):
        data = {'interface': name[0], 'nick': name[1], 'name': "__".join(name),
        'kind': kind, 'type': "_".join(name)}
        return self.tpl_message_info % data

    def structure_members(self, name, definition=False):
        desc = ''
        for uid, arg in enumerate(self.structures[name]):
            if definition:
                desc += self.definition_structure_member(name, arg, uid + 1)
            else:
                desc += self.structure_member(name, uid + 1)
        return desc

    def structure_member(self, name, uid):
        data = {'type': self.type_parameter, 'name': "__".join(name), 'id': uid}
        return self.tpl_structure_member % data

    def definition_structure_member(self, name, arg, uid):
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
        desc += self.tpl_definition_structure_member % data
        return desc

    def function_array_parameters(self, name, kind):
        args = self.function_members(name, kind)
        data = {'type': self.type_parameter, 'name': "__".join(name), 'kind': kind, 'args': args}
        return self.tpl_definition_function % data

    def function_members(self, name, kind, definition=False):
        desc = ''
        uid = 1
        for arg in self.args[name]:
            if kind == 'request' and arg.direction != TypeArgument.Input: continue
            if kind == 'response' and arg.direction != TypeArgument.Output: continue
            if definition:
                desc += self.definition_function_member(name, arg, kind, uid)
            else:
                desc += self.function_member(name, kind, uid)
            uid = uid + 1
        return desc

    def function_member(self, name, kind, uid):
        data = {'type': self.type_parameter, 'name': "__".join(name), 'kind': kind, 'id': uid}
        return self.tpl_function_member % data

    def definition_function_member(self, name, arg, kind, uid):
        desc = ''
        type_parameter = self.type_parameter
        info = self.parameter_info(name, arg, uid)
        if arg.isArray():
           desc += self.parameter_array(name, arg, uid, kind)
           type_parameter = self.type_array
           info = self.parameter_array_info(name, arg, uid, kind)
        elif arg.type() in self.signatures:
           type_parameter = self.type_structure
           info = self.parameter_structure_info(name, arg, uid)
        data = {'type': type_parameter, 'name': "__".join(name), 'kind': kind, 'id': uid, 'info': info}
        desc += self.tpl_definition_function_member % data
        return desc

    def parameter_info(self, name, arg, uid, mandatory=None):
        mandatory = 'true' if mandatory or arg.isMandatory() else 'false'
        data = {'name': arg.name(), 'type': self.arrayType(arg), 'mandatory': mandatory}
        return self.tpl_parameter_info % data

    def parameter_array_info(self, name, arg, uid, kind=''):
        mandatory = 'true' if arg.isMandatory() else 'false'
        data = {'name': arg.name(), 'type': self.fulltype(arg), 'mandatory': mandatory,
        'array': self.parameter_array_item(name, arg, uid, kind), 'introspection': self.arraySignature(arg)}
        return self.tpl_parameter_array_info % data

    def parameter_array_item(self, name, arg, uid, kind=''):
        if kind != '': kind += '__'
        data = {'type': self.type_parameter, 'name': "__".join(name), 'id': uid, 'kind': kind}
        return self.tpl_parameter_array_item % data

    def parameter_structure_info(self, name, arg, uid, mandatory=None):
        mandatory = 'true' if mandatory or arg.isMandatory() else 'false'
        data = {'name': arg.name(), 'type': self.arrayType(arg), 'mandatory': mandatory,
        'struct': arg.type().replace('.', "__")}
        return self.tpl_parameter_structure_info % data

    def parameter_array(self, name, arg, uid, kind=''):
        if kind != '': kind += '__'
        type_parameter = self.type_parameter
        info = self.parameter_info(name, arg, uid, True)
        if arg.type() in self.signatures:
            type_parameter = self.type_structure
            info = self.parameter_structure_info(name, arg, uid, True)
        data = {'type': type_parameter, 'name': "__".join(name), 'id': uid, 'info': info, 'kind': kind}
        return self.tpl_parameter_array % data

    def structure_array_parameters(self, name):
        data = {'type': self.type_parameter, 'name': "__".join(name), 'args': self.structure_members(name)}
        return self.tpl_definition_structure % data

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
