from __future__ import print_function
import os
from datetime import date
from Header import CppWarning
from Header import CppHeader

class CppDescription(object):
    generator = os.path.basename(__file__)
    include = "#include \"dbus/message_descriptions.h\""

    def __init__(self, desc):
        self.desc = desc

    def write(self, filename):
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
