from collections import OrderedDict
from protocol import Visitor, TypeArgument

class RequestToSdlVisitor(Visitor):
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

    tpl_new_interface = '  %(name)s = new QDBusInterface("com.ford.sdl.core", "/", "com.ford.sdl.core.%(name)s", bus, this);'

    tpl_delete_interface = '  %(name)s->deleteLater();'

    tpl_fill_arg = '  %(type)s %(name)s_tmp;\n  if (%(condition)s) {\n%(positive)s\n  } else {\n%(negative)s\n  }\n'

    tpl_condition = 'VariantToValue(%(name)s, %(name)s_tmp)'

    tpl_negative = '    LOG4CXX_ERROR(logger_, "%(name)s in %(interface)s_%(parent)s is NOT valid");\n    return false;'

    tpl_positive = '%(data)s    args << QVariant::fromValue(%(name)s_tmp);'

    tpl_optional = '    if (%(name)s_tmp.presence) {\n%(bounds)s    }\n'

    tpl_new_delete = 'RequestToSDL::RequestToSDL(QObject *parent) {\n  QDBusConnection bus = QDBusConnection::sessionBus();\n%(news)s\n}\n\nRequestToSDL::~RequestToSDL() {\n%(deletes)s\n  this->deleteLater();\n}\n'

    tpl_request = 'bool RequestToSDL::%(name)s(%(args)sQ%(prefix)sValue hmi_callback) {\n  LOG4CXX_TRACE(logger_, "ENTER");\n  QList<QVariant> args;\n%(fills)s  new requests::%(name)s(hmi_callback, %(interface)s , args, "%(rpc)s");\n  LOG4CXX_TRACE(logger_, "EXIT");\n  return true;\n}\n'

    create_logger = '\nCREATE_LOGGERPTR_GLOBAL(logger_, "DBusPlugin")\n'

    tpl_interface = '  QDBusInterface *%s;'

    tpl_invokable = '  Q_INVOKABLE bool %(name)s(%(args)sQ%(prefix)sValue hmi_callback);'

    tpl_logmessage = '      LOG4CXX_ERROR(logger_, "%s in %s out of bounds");\n      return false;\n'

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


    def interfaces(self):
        return '\n'.join([ self.tpl_interface % i for i in self.ifaces ])

    def invokables(self):
        return '\n'.join([ self.prepare_invokable(m) for m in self.methods ])

    def prepare_invokable(self, method):
        return self.tpl_invokable % {'name': '_'.join(method), 'args': self.prepare_args(method), 'prefix': self.prefix}

    def prepare_args(self, method):
        params = [ 'QVariant %s,' % arg.name() for arg in self.args[method] if arg.direction == TypeArgument.Input ]
        if len(params) > 0:
           return ''.join(params)
        return ''

    def new_interfaces(self):
        return '\n'.join([ self.tpl_new_interface % {'name': i} for i in self.ifaces ])

    def delete_interfaces(self):
        return '\n'.join([ self.tpl_delete_interface % {'name': i} for i in self.ifaces ])

    def fill_args(self, method):
        return ''.join([ self.tpl_fill_arg % {'type': self.qt_param_type(arg), 'name': arg.name(), 'condition': self.condition(arg), 'positive': self.positive(arg), 'negative': self.negative(arg)} for arg in self.args[method] if arg.direction == TypeArgument.Input ])

    def condition(self, arg):
        return self.tpl_condition % {'name': arg.name()}

    def positive(self, arg):
        return self.tpl_positive % {'name': arg.name(), 'data': self.validation('%s_tmp' % arg.name(),arg)}

    def negative(self, arg):
        return self.tpl_negative % {'name': arg.name(), 'interface': arg.interface(), 'parent': arg.parent()}

    def bounds(self, name, arg):
        if arg.isArray():
            return self.bounds_array(name, arg)
        elif arg.isStruct():
            struct = self.struts[(arg.interface(), arg.name())]
            return ''.join([ self.validation('%s.%s' % (name, p.name()), p) for p in struct ])
        else:
            return self.bounds_basic(name, arg)

    def bounds_array(self, name, arg):
        conds = ''
        if arg.minsize() > 0:
            conds += '    if (%s.count() < %d) {      \n%s    }\n' % (name, arg.minsize(), self.logmessage(arg))
        if arg.maxsize() > 0:
            conds += '    if (%s.count() > %d) {      \n%s    }\n' % (name, arg.maxsize(), self.logmessage(arg))
        if arg.restricted():
            pass
        return conds

    def bounds_basic(self, name, arg):
        argtype = arg.type()
        if argtype in ('Integer', 'Float'):
            conds = []
            if arg.minvalue() is not None:
               conds.append('(%s < %d)' % (name, arg.minvalue()))
            if arg.maxvalue() is not None:
               conds.append('(%s > %d)' % (name, arg.maxvalue()))
            return '    if (%s) {      \n%s    }\n' % (' || '.join(conds), self.logmessage(arg))
        if argtype == 'String':
            conds = []
            if arg.minlength() > 0:
               conds.append('(%s.size() < %d)' % (name, arg.minlength()))
            if arg.maxlength() > 0:
               conds.append('(%s.size() > %d)' % (name, arg.maxlength()))
            return '    if (%s) {      \n%s    }\n' % (' || '.join(conds), self.logmessage(arg))
        return ''

    def logmessage(self, arg):
        return self.tpl_logmessage % (arg.name(), arg.parent())

    def validation(self, name, arg):
        if arg.isMandatory():
            return self.bounds(name, arg)
        else:
            return self.tpl_optional % { 'name': arg.name(), 'bounds': self.bounds(name + '.val', arg) }

    def requestclass(self):
        return self.tpl_classRequestToSDL % (self.invokables(), self.interfaces())

    def logger(self):
        return self.create_logger

    def requestsource(self):
        return self.tpl_new_delete % {'news': self.new_interfaces(), 'deletes': self.delete_interfaces()}

    def requests(self):
        return [ self.tpl_request % {'name': '_'.join(m), 'args': self.prepare_args(m).replace(',', ', '), 'prefix': self.prefix, 'fills': self.fill_args(m), 'interface': m[0], 'rpc': m[1]} for m in self.methods ]
