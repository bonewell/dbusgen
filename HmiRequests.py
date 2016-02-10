from saver import AbstractSaver, HeaderWriter, SourceWriter
from header import CppWarning, CppHeader

class HmiRequests(AbstractSaver):
    filename = 'hmi_requests'
    guard = "SRC_COMPONENTS_QTHMI_QMLMODELQT5_HMIREQUESTS_"
    includes = [ "<QObject>", "<QJSValue>", "<QDBusPendingCall>", "<QDBusPendingCallWatcher>",
    "<QDBusPendingReply>", "<QDBusAbstractInterface>", "<QDBusInterface>", "<QJSEngine>", '"qml_dbus.h"' ]
    namespace = 'requests'

    tpl_template = "template<>\nQJSValue HMIRequest::CreateQJSValue(%s_%s value);\n"

    classHmiRequest = '''class HMIRequest: public QObject {
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

    def write(self, path):
        self.writeHeader(path)
        self.writeSource(path)

    def writeHeader(self, path):
        info = HeaderWriter.Metadata(__file__, self.guard, self.includes, self.namespace)
        with HeaderWriter(self.filename, path, info) as writer:
            writer.write(self.classHmiRequest)
            map(lambda s: writer.write(self.tpl_template % s), self.data.structures)
            map(lambda m: writer.write(self.tpl_request % (m + m)), self.data.methods)

    def writeSource(self, path):
        info = SourceWriter.Metadata(__file__, ['"%s.h"' % self.filename], self.namespace)
        with SourceWriter(self.filename, path, info) as writer:
            map(lambda s: writer.write(self.tpl_template_cpp % (s + (self.data.params(s),))), self.data.structures)
            writer.write(self.cppHmiRequest)
            map(lambda m: writer.write(self.tpl_request_cpp % (m + (self.data.func_params(m), self.data.prepared_params(m)))), self.data.methods)
