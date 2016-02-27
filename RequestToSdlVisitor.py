from collections import OrderedDict
from protocol import Visitor, TypeArgument

class RequestToSdlVisitor(Visitor):
    tpl_list_params = '  object.setProperty("%s", %s);\n'

    tpl_list_params_value_mandatory = 'CreateQJSValue(value.%s)'

    tpl_list_params_value = 'value.%s.presence ? CreateQJSValue(value.%s.val) : QJSValue()'

    tpl_mandatory_param = '\n  param = CreateQJSValue(reply.argumentAt<%d>());'

    tpl_optional_param = '\n  if (reply.argumentAt<%d>().presence) {\n    param = CreateQJSValue(reply.argumentAt<%d>().val);\n  } else {\n    param = QJSValue();\n  }'

    tpl_classRequestToSDL = '''class QDBusInterface;
class RequestToSDL : public QObject
{
  Q_OBJECT
 public:
  explicit RequestToSDL(QObject *parent = 0);
  ~RequestToSDL();
%s
 private:
%s
};'''

    create_logger = '\nCREATE_LOGGERPTR_GLOBAL(logger_, "DBusPlugin")\n'

    def __init__(self, version="5.1.0", logs=False):
        self.enums = []
        self.names = []
        self.ifaces = []
        self.structures = OrderedDict()
        self.methods = OrderedDict()
        self.args = OrderedDict()
        self.logs = logs
        self.check(version)

    def check(self, version):
        if version == "5.1.0":
            self.prefix = 'JS'
            self.conntype = 'BlockingQueued'
        elif version == "4.8.5":
            self.prefix = 'Script'
            self.conntype = 'Direct'
        else:
           raise RuntimeError("Unsupported Qt version")

    def visitProtocol(self, protocol):
        if self.logs: print('Visit protocol')
        return True

    def visitInterface(self, iface):
        if self.logs: print('Visit interface %s' % iface.name())
        self.ifaces.append(iface.name())
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

    tpl_interface = '  QDBusInterface *%s;'
    tpl_invokable = '  Q_INVOKABLE bool %s_%s(%sQ%sValue hmi_callback);'

    def interfaces(self):
        return '\n'.join([ self.tpl_interface % i for i in self.ifaces ])

    def invokables(self):
        return '\n'.join([ self.prepare_invokable(m) for m in self.methods ])

    def prepare_invokable(self, method):
        return self.tpl_invokable % (method + (self.prepare_args(method), self.prefix))

    def prepare_args(self, method):
        params = [ 'QVariant %s,' % arg.name() for arg in self.args[method] if arg.direction == TypeArgument.Input ]
        if len(params) > 0:
           return ''.join(params)
        return ''

    tpl_new_interface = '  %s = new QDBusInterface("com.ford.sdl.core", "/", "com.ford.sdl.core.%s", bus, this);'

    tpl_delete_interface = '  %s->deleteLater();'

    tpl_fill_arg = '  %s %s_tmp;\n  if (%s) {\n%s\n  } else {\n%s\n  }\n'
    
    tpl_condition = 'VariantToValue(%s, %s_tmp)'

    tpl_negative = '    LOG4CXX_ERROR(logger_, "%s in %s_%s is NOT valid");\n    return false;'

    tpl_positive = '%s    args << QVariant::fromValue(%s_tmp);'

    tpl_validation = ''

    tpl_new_delete = 'RequestToSDL::RequestToSDL(QObject *parent) {\n  QDBusConnection bus = QDBusConnection::sessionBus();\n%s\n}\n\nRequestToSDL::~RequestToSDL() {\n%s\n  this->deleteLater();\n}\n'

    tpl_request = 'bool RequestToSDL::%s_%s(%sQ%sValue hmi_callback) {\n  LOG4CXX_TRACE(logger_, "ENTER");\n  QList<QVariant> args;\n%s  new requests::%s_%s(hmi_callback, %s , args, "%s");\n  LOG4CXX_TRACE(logger_, "EXIT");\n  return true;\n}\n'

    def new_interfaces(self):
        return '\n'.join([ self.tpl_new_interface % (i, i) for i in self.ifaces ])

    def delete_interfaces(self):
        return '\n'.join([ self.tpl_delete_interface % i for i in self.ifaces ])

    def fill_args(self, method):
        return ''.join([ self.tpl_fill_arg % (self.qt_param_type(arg), arg.name(), self.condition(arg), self.positive(arg), self.negative(arg)) for arg in self.args[method] if arg.direction == TypeArgument.Input ])

    def condition(self, arg):
        return self.tpl_condition % (arg.name(), arg.name())

    def positive(self, arg):
        return self.tpl_positive % (self.validation(arg), arg.name())

    def negative(self, arg):
        return self.tpl_negative % (arg.name(), arg.interface(), arg.parent())

    def validation(self, arg):
        return self.tpl_validation

    def requestclass(self):
        return self.tpl_classRequestToSDL % (self.invokables(), self.interfaces())

    def logger(self):
        return self.create_logger

    def requestsource(self):
        return self.tpl_new_delete % (self.new_interfaces(), self.delete_interfaces())

    def requests(self):
        return [ self.tpl_request % (m + (self.prepare_args(m).replace(',', ', '), self.prefix, self.fill_args(m)) + m + m) for m in self.methods ]
