from collections import OrderedDict
from protocol import Visitor, TypeArgument

class HmiRequestsVisitor(Visitor):
    base_class = '''class HMIRequest: public QObject {
  Q_OBJECT
public:
  HMIRequest(QJSValue hmi_callback, QDBusInterface *interface, QList<QVariant> args, QString name );
protected:
  virtual QJSValueList fillArgsList() = 0;
  QDBusPendingCallWatcher *watcher_;
  QJSValue hmi_callback_;
  
  template<typename T>
  QJSValue CreateQJSValue(T value) {
    return QJSValue(value);
  }
  
  template<typename T>
  QJSValue CreateQJSValue(QList<T> value) {
    QJSValue array = hmi_callback_.engine()->newArray();
    int i = 0;
    foreach (T item, value) {
      QJSValue value = CreateQJSValue(item);
      array.setProperty(i, value);
      ++i;
    }
    return array;
  }
private:
  QDBusInterface *interface_;
  QList<QVariant> args_;
public slots:
  void invokeCallback();
};'''

    qstringlist = "template<>\nQJSValue HMIRequest::CreateQJSValue(QStringList value);"

    constructor = '''HMIRequest::HMIRequest(QJSValue hmi_callback, QDBusInterface *interface, QList<QVariant> args, QString name) :
      hmi_callback_(hmi_callback), interface_(interface), args_(args) {
  QDBusPendingCall pcall = interface->asyncCallWithArgumentList(name, args);
  watcher_ = new QDBusPendingCallWatcher(pcall);
  QObject::connect(watcher_, SIGNAL(finished(QDBusPendingCallWatcher*)), this, SLOT(invokeCallback()));
  }\n'''

    invoker = '''void HMIRequest::invokeCallback() {
  if (!hmi_callback_.isUndefined()) {
    QJSValueList qjsValueList;
    qjsValueList = this->fillArgsList();
    hmi_callback_.call(qjsValueList);
  }
  watcher_->deleteLater();
  this->deleteLater();
  }
  '''

    tpl_template = "template<>\nQJSValue HMIRequest::CreateQJSValue(%(name)s value);\n"

    tpl_template_cpp = "template<>\nQJSValue HMIRequest::CreateQJSValue(%(name)s value){\n  QJSValue object = hmi_callback_.engine()->newObject();\n%(body)sreturn object;\n}\n"

    tpl_request = '''class %(name)s: public HMIRequest {
  Q_OBJECT
 public:
  %(name)s(QJSValue hmi_callback, QDBusInterface *interface, QList<QVariant> args, QString name):
    HMIRequest(hmi_callback, interface, args, name) {}
 private:
  QJSValueList fillArgsList();
  };
  '''

    tpl_list_params = '  object.setProperty("%(name)s", %(value)s);\n'

    tpl_list_params_value_mandatory = 'CreateQJSValue(value.%(name)s)'

    tpl_list_params_value = 'value.%(name)s.presence ? CreateQJSValue(value.%(name)s.val) : QJSValue()'

    tpl_mandatory_param = '\n  param = CreateQJSValue(reply.argumentAt<%(uid)d>());'

    tpl_optional_param = '\n  if (reply.argumentAt<%(uid)d>().presence) {\n    param = CreateQJSValue(reply.argumentAt<%(uid)d>().val);\n  } else {\n    param = QJSValue();\n  }'

    tpl_fillargslist = 'QJSValueList %(name)s::fillArgsList() {\n  QDBusPendingReply< %(params)s > reply = *watcher_;\n  QJSValueList qjsValueList;\n  \n  QJSValue param;\n  %(filling)s\n  return qjsValueList;\n}\n'

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

    def baseclass(self):
        return self.base_class + '\n\n' + self.qstringlist

    def templates(self):
        return [ self.tpl_template % { 'name': '_'.join(s) } for s in self.structures ]

    def bodytemplates(self):
        return [ self.tpl_template_cpp % { 'name': '_'.join(s), 'body': self.params(s) } for s in self.structures ]

    def requests(self):
        return [ self.tpl_request % { 'name': '_'.join(m) } for m in self.methods ]

    def basemethods(self):
        return self.constructor + '  \n' + self.invoker

    def param(self, arg):
        return self.tpl_list_params % { 'name': arg.name(), 'value': self.param_value(arg) }

    def params(self, struct):
        params = [ self.param(p) for p in self.structures[struct] ]
        return ''.join(params)

    def param_value(self, arg):
        if arg.isMandatory():
            return self.tpl_list_params_value_mandatory % { 'name': arg.name() }
        else:
            return self.tpl_list_params_value % { 'name': arg.name() }

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
            text = self.tpl_mandatory_param % { 'uid': self.uid }
        else:
            text = self.tpl_optional_param % { 'uid': self.uid }
        text += '\n  qjsValueList.append(param);'
        self.uid += 1
        return text

    def func_params(self, method):
        return ','.join([ self.qt_param_type(p) for p in self.args[method] if p.direction == TypeArgument.Output])

    def prepared_params(self, method):
        self.uid = 0
        return ''.join([ self.prepare_param(p) for p in self.args[method] if p.direction == TypeArgument.Output])

    def fillers(self):
        return [ self.tpl_fillargslist % { 'name': '_'.join(m), 'params': self.func_params(m), 'filling': self.prepared_params(m) } for m in self.methods ]
