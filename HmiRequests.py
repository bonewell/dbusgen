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

    tpl_template_cpp = "template<>\nQJSValue HMIRequest::CreateQJSValue(%s_%s value){\n  QJSValue object = hmi_callback_.engine()->newObject();\n%sreturn object;\n}\n"

    cppHmiRequest = '''HMIRequest::HMIRequest(QJSValue hmi_callback, QDBusInterface *interface, QList<QVariant> args, QString name) :
      hmi_callback_(hmi_callback), interface_(interface), args_(args) {
  QDBusPendingCall pcall = interface->asyncCallWithArgumentList(name, args);
  watcher_ = new QDBusPendingCallWatcher(pcall);
  QObject::connect(watcher_, SIGNAL(finished(QDBusPendingCallWatcher*)), this, SLOT(invokeCallback()));
  }
  
void HMIRequest::invokeCallback() {
  if (!hmi_callback_.isUndefined()) {
    QJSValueList qjsValueList;
    qjsValueList = this->fillArgsList();
    hmi_callback_.call(qjsValueList);
  }
  watcher_->deleteLater();
  this->deleteLater();
  }
  '''

    tpl_request_cpp = 'QJSValueList %s_%s::fillArgsList() {\n  QDBusPendingReply< %s > reply = *watcher_;\n  QJSValueList qjsValueList;\n  \n  QJSValue param;\n  %s\n  return qjsValueList;\n}\n'

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
        print('#include "hmi_requests.h"\n')
        print("namespace requests {")
        for s in self.data.structures:
            print(self.tpl_template_cpp % (s + (self.data.params(s),)))
        print(self.cppHmiRequest)
        for m in self.data.methods:
            print(self.tpl_request_cpp % (m + (self.data.func_params(m), self.data.prepared_params(m))))
        print("}  // namespace requests")
        fd.close()
