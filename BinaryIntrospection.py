from datetime import date
from Header import CppWarning
from Header import CppHeader

class BinaryIntrospection(object):
    prefix = 'char introspection_xml[] = {'

    suffix = ' 0x00\n};'

    def __init__(self, dbus):
        self.dbus = dbus

    def write(self, filename):
        fd = open(filename, 'w')
        fd.write(CppWarning % "BinaryIntrospection.py")
        fd.write(CppHeader % date.today().year)
        fd.write(self.prefix)
        fd.write(self.convert())
        fd.write(self.suffix)
        fd.close()

    def convert(self):
        cnt = 0
        value = ''
        for char in self.dbus.xml():
            if cnt % 12 == 0:
                value += '\n  '
            else:
                value += ' '
            value += '0x%02x,' % ord(char)
            cnt += 1
        return value
