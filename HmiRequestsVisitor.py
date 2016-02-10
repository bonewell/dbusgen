from collections import OrderedDict
from protocol import Visitor, TypeArgument

class HmiRequestsVisitor(Visitor):
    tpl_list_params = '  object.setProperty("%s", %s);\n'

    tpl_list_params_value_mandatory = 'CreateQJSValue(value.%s)'

    tpl_list_params_value = 'value.%s.presence ? CreateQJSValue(value.%s.val) : QJSValue()'

    tpl_mandatory_param = '\n  param = CreateQJSValue(reply.argumentAt<%d>());'

    tpl_optional_param = '\n  if (reply.argumentAt<%d>().presence) {\n    param = CreateQJSValue(reply.argumentAt<%d>().val);\n  } else {\n    param = QJSValue();\n  }'

    def __init__(self, logs=False):
        self.enums = []
        self.names = []
        self.structures = OrderedDict()
        self.methods = OrderedDict()
        self.args = OrderedDict()
        self.logs = logs

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
        self.structures[(struct.interface(), struct.name())] = []
        self.names.append('.'.join(fullname))
        return True

    def visitSignal(self, signal):
        fullname = (signal.interface(), signal.name())
        if self.logs: print('Visit signal %s' % '.'.join(fullname))
        return False

    def visitMethod(self, method):
        fullname = (method.interface(), method.name())
        if self.logs: print('Visit method %s' % '.'.join(fullname))
        if method.provider() == 'sdl':
            self.methods[(method.interface(), method.name())] = method
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


    def params(self, struct):
        text = ''
        for p in self.structures[struct]:
            text += self.tpl_list_params % (p.name(), self.param_value(p))
        return text

    def param_value(self, arg):
        if arg.isMandatory():
            return self.tpl_list_params_value_mandatory % arg.name()
        else:
            return self.tpl_list_params_value % (arg.name(), arg.name())

    def qt_param_type(self, arg):
        typename = arg.type()
        if typename == 'Integer': code = 'int'
        elif typename == 'String': code = 'QString'
        elif typename == 'Boolean': code = 'bool'
        elif typename == 'Float': code = 'double'
        elif typename in self.enums: code = 'int'
        elif typename in self.names: code = arg.fulltype().replace('.', '_')
        else:
            raise RuntimeError('Unknown type: %s - %s' % (typename, self.names))
        if arg.isArray():
            if typename == 'String':
                code = 'QStringList'
            else:
                code = 'QList< %s >' % code
        if not arg.isMandatory():
            code = 'OptionalArgument< %s >' % code
        return code


    def prepare_param(self, arg):
        if arg.isMandatory():
            text = self.tpl_mandatory_param % self.uid
        else:
            text = self.tpl_optional_param % (self.uid, self.uid)
        text += '\n  qjsValueList.append(param);'
        self.uid += 1
        return text

    def func_params(self, method):
        return ','.join([ self.qt_param_type(p) for p in self.args[method] if p.direction == TypeArgument.Output])

    def prepared_params(self, method):
        self.uid = 0
        return ''.join([ self.prepare_param(p) for p in self.args[method] if p.direction == TypeArgument.Output])
