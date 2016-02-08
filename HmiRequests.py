from __future__ import print_function
import os
from datetime import date
from Header import CppWarning
from Header import CppHeader

class HmiRequests(object):
    generator = os.path.basename(__file__)

    guard = "SRC_COMPONENTS_QTHMI_QMLMODELQT5_HMIREQUESTS_"

    includes = [ "<QObject>", "<QJSValue>", "<QDBusPendingCall>", "<QDBusPendingCallWatcher>",
    "<QDBusPendingReply>", "<QDBusAbstractInterface>", "<QDBusInterface>", "<QJSEngine>", '"qml_dbus.h"' ]

    tpl_template = "template<>\nQJSValue HMIRequest::CreateQJSValue(%s_%s value);\n"

    classHmiRequest = '''
namespace requests {
class HMIRequest: public QObject {
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
};

template<>
QJSValue HMIRequest::CreateQJSValue(QStringList value);'''

    tpl_request = '''class %s_%s: public HMIRequest {
  Q_OBJECT
 public:
  %s_%s(QJSValue hmi_callback, QDBusInterface *interface, QList<QVariant> args, QString name):
    HMIRequest(hmi_callback, interface, args, name) {}
 private:
  QJSValueList fillArgsList();
  };
  '''

    def __init__(self, data):
        self.data = data

    def writeHeader(self, filename):
        fd = open(filename, 'w')
        os.sys.stdout = fd
        print(CppWarning % self.generator)
        print(CppHeader % date.today().year)
        print("#ifndef %s\n#define %s\n" % (self.guard, self.guard))
        for i in self.includes:
            print("#include %s" % i)
        print(self.classHmiRequest)
        for s in self.data.structures:
            print(self.tpl_template % s)
        for m in self.data.methods:
            print(self.tpl_request % (m + m))
        print("}  // namespace requests")
        print("#endif  // %s" % self.guard)
        fd.close()

    def writeSource(self, filename):
        fd = open(filename, 'w')
        os.sys.stdout = fd
        print(CppWarning % self.generator)
        print(CppHeader % date.today().year)
        fd.close()


    def __A(self):
        fd = open(filename, 'w')
        os.sys.stdout = fd
        print(CppWarning % self.generator)
        print(CppHeader % date.today().year)
        print(self.include, end="\n\n")

        print("namespace {", end="\n\n")
        print(self.desc.structs(), end="\n\n")
        for name in self.desc.names:
            print(self.desc.definition(name), end="\n\n")
        print("}", end="\n\n")

        data = (self.desc.namespace, self.desc.messages())
        print("namespace %s {\n\n%s\n}" % data, end="\n\n")
        fd.close()
