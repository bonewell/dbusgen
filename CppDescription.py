from datetime import date
from Header import CppWarning
from Header import CppHeader

class CppDescription(object):
    include = "#include \"dbus/message_descriptions.h\"\n\n"

    def __init__(self, desc):
        self.desc = desc

    def write(self, filename):
        fd = open(filename, 'w')
        fd.write(CppWarning % "CppDescription.py")
        fd.write(CppHeader % date.today().year)
        fd.write(self.include)

        fd.write("namespace {\n\n")
        fd.write(self.desc.structs())
        fd.write("\n\n")
        for name in self.desc.names:
            fd.write(self.desc.definition(name))
            fd.write("\n\n")
        fd.write("}\n\n")

        data = (self.desc.namespace, self.desc.messages())
        fd.write("namespace %s {\n\n%s\n}\n\n" % data)
        fd.close()
