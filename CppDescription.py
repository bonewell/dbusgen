from saver import AbstractSaver
from saver import SourceWriter

class CppDescription(AbstractSaver):
    filename = 'message_descriptions'
    include = '"dbus/message_descriptions.h"\n'

    def __init__(self, desc):
        self.desc = desc

    def write(self, path):
        info = SourceWriter.Metadata(__file__, [ self.include ])
        with SourceWriter(self.filename, path, info) as writer:
            writer.write("namespace {\n")
            writer.write(self.desc.structs())
            map(lambda n: writer.write(self.desc.definition(n)), self.desc.names)
            writer.write("}\n")
            data = (self.desc.namespace, self.desc.messages())
            writer.write("namespace %s {\n\n%s\n}\n" % data)
