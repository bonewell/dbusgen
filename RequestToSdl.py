from __future__ import print_function
import os
from datetime import date
from Header import CppWarning
from Header import CppHeader

class RequestToSdl(object):
    generator = os.path.basename(__file__)

    guard = "SRC_COMPONENTS_QT_HMI_QML_PLUGINS_DBUS_ADAPTER_REQUEST_TO_SDL_H_"

    includes_header = [ "<QtCore/QObject>", "<QtCore/QVariant>", "<QtCore/QStringList>\n", '"qml_dbus.h"\n' ]

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

    includes_source = [ '"request_to_sdl.h"', "<QtDBus/QDBusConnection>", "<QtDBus/QDBusInterface>", '"hmi_requests.h"', '"utils/logger.h"' ]

    tpl_new_delete = 'RequestToSDL::RequestToSDL(QObject *parent) {\n  QDBusConnection bus = QDBusConnection::sessionBus();\n%s\n}\n\nRequestToSDL::~RequestToSDL() {\n%s\n  this->deleteLater();\n}\n'

    tpl_request = 'bool RequestToSDL::%s_%s(%sQ%sValue hmi_callback) {\n  LOG4CXX_TRACE(logger_, "ENTER");\n  QList<QVariant> args;\n%s  new requests::%s_%s(hmi_callback, %s , args, "%s");\n  LOG4CXX_TRACE(logger_, "EXIT");\n  return true;\n}\n'

    def __init__(self, version, data):
        self.data = data
        if version == "5.1.0":
           self.prefix = 'JS'
           self.includes_header.append("<QtQml/QJSValue>")
        elif version == "4.8.5":
           self.prefix = 'Script'
           self.includes_header.append("<QtScript/QScriptValue>")

    def writeHeader(self, filename):
        fd = open(filename, 'w')
        os.sys.stdout = fd
        print(CppWarning % self.generator)
        print(CppHeader % date.today().year)
        print("#ifndef %s\n#define %s\n" % (self.guard, self.guard))
        for i in self.includes_header:
            print("#include %s" % i)
        print(self.tpl_classRequestToSDL % (self.data.invokables(), self.data.interfaces()))
        print("#endif  // %s" % self.guard, end='')
        fd.close()

    def writeSource(self, filename):
        fd = open(filename, 'w')
        os.sys.stdout = fd
        print(CppWarning % self.generator)
        print(CppHeader % date.today().year)
        for i in self.includes_source:
            print('#include %s' % i)
        print('\nCREATE_LOGGERPTR_GLOBAL(logger_, "DBusPlugin")\n')
        print(self.tpl_new_delete % (self.data.new_interfaces(), self.data.delete_interfaces()))
        for m in self.data.methods:
            print(self.tpl_request % (m + (self.data.prepare_args(m).replace(',', ', '), self.prefix, self.data.fill_args(m)) + m + m))
        fd.close()
