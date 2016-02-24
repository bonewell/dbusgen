from saver import AbstractSaver
from saver import HeaderWriter
from saver import SourceWriter

class RequestToSdl(AbstractSaver):
    filename = 'request_to_sdl'
    guard = "SRC_COMPONENTS_QT_HMI_QML_PLUGINS_DBUS_ADAPTER_REQUEST_TO_SDL_H_"
    includes_header = [ "<QtCore/QObject>", "<QtCore/QVariant>", "<QtCore/QStringList>\n", '"qml_dbus.h"\n' ]
    includes_source = [ '"request_to_sdl.h"', "<QtDBus/QDBusConnection>", "<QtDBus/QDBusInterface>", '"hmi_requests.h"', '"utils/logger.h"' ]

    def __init__(self, data, version="5.1.0"):
        self.data = data
        if version == "5.1.0":
           self.includes_header.append("<QtQml/QJSValue>")
        elif version == "4.8.5":
           self.includes_header.append("<QtScript/QScriptValue>")
        else:
           raise RuntimeError("Unsupported Qt version")

    def write(self, path):
        self.writeHeader(path)
        self.writeSource(path)

    def writeHeader(self, path):
        info = HeaderWriter.Metadata(__file__, self.guard, self.includes_header)
        with HeaderWriter(self.filename, path, info) as writer:
            writer.write(self.data.requestclass())

    def writeSource(self, path):
        info = SourceWriter.Metadata(__file__, self.includes_source)
        with SourceWriter(self.filename, path, info) as writer:
            writer.write(self.data.logger())
            writer.write(self.data.requestsource())
            map(lambda r: writer.write(r), self.data.requests())
