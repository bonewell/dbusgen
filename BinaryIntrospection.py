from __future__ import print_function
import os
from datetime import date
from Header import CppWarning
from Header import CppHeader

class BinaryIntrospection(object):
    generator = os.path.basename(__file__)
    prefix = 'char introspection_xml[] = {'
    suffix = ' 0x00\n};'

    def __init__(self, dbus):
        self.dbus = dbus

    def write(self, filename):
        fd = open(filename, 'w')
        os.sys.stdout = fd
        print(CppWarning % self.generator)
        print(CppHeader % date.today().year)
        print(self.prefix, end='')
        print(self.convert(), end='')
        print(self.suffix, end='')
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
