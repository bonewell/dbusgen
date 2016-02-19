from saver import AbstractSaver
from saver import HeaderWriter
from saver import SourceWriter

class HmiRequests(AbstractSaver):
    filename = 'hmi_requests'
    guard = "SRC_COMPONENTS_QTHMI_QMLMODELQT5_HMIREQUESTS_"
    includes = [ "<QObject>", "<QJSValue>", "<QDBusPendingCall>", "<QDBusPendingCallWatcher>",
    "<QDBusPendingReply>", "<QDBusAbstractInterface>", "<QDBusInterface>", "<QJSEngine>", '"qml_dbus.h"' ]
    namespace = 'requests'
    

    def __init__(self, data):
        self.data = data

    def write(self, path):
        self.writeHeader(path)
        self.writeSource(path)

    def writeHeader(self, path):
        info = HeaderWriter.Metadata(__file__, self.guard, self.includes, self.namespace)
        with HeaderWriter(self.filename, path, info) as writer:
            writer.write(self.data.baseclass())
            map(lambda s: writer.write(s), self.data.templates())
            map(lambda r: writer.write(r), self.data.requests())

    def writeSource(self, path):
        info = SourceWriter.Metadata(__file__, ['"%s.h"' % self.filename], self.namespace)
        with SourceWriter(self.filename, path, info) as writer:
            map(lambda s: writer.write(s), self.data.bodytemplates())
            writer.write(self.data.basemethods())
            map(lambda f: writer.write(f), self.data.fillers())
