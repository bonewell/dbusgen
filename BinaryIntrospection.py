from saver import AbstractSaver
from saver import SourceWriter

class BinaryIntrospection(AbstractSaver):
    filename = 'introspection_xml'
    prefix = 'char introspection_xml[] = {\n  '
    suffix = '};'
    length = 12 # count of chars in a line to devide

    def __init__(self, dbus):
        self.dbus = dbus

    def write(self, path):
        info = SourceWriter.Metadata(__file__)
        with SourceWriter(self.filename, path, info) as writer:
            writer.write(self.prefix, end='')
            writer.write(self.convert())
            writer.write(self.suffix, end='')

    def convert(self):
        chars = [ '0x%02x' % ord(c) for c in self.dbus.xml() ] + ['0x00']
        step = self.length
        lines = [', '.join(chars[i:i + step]) for i in range(0, len(chars), step)]
        return ',\n  '.join(lines)
