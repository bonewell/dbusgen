from operator import methodcaller
from saver import AbstractSaver
from saver import QmlWriter
from saver import JSWriter

class QmlDBusQml(AbstractSaver):
    tpl_filename = '%sProxy'
    parent = 'Item'
    imports = [ '"Common.js" as Common', '".."' ]

    tpl_subitem = '  %(name)s {\n    id: sdl%(name)s\n  }'

    def __init__(self, data, version="5.1.0"):
        self.data = data
        v = '1.1' if version == '4.8.5' else '2.0'
        self.imports = ['QtQuick %s' % v] + self.imports

    def write(self, path):
        self.path = path
        map(self.writeController, self.data.ifaces)
        map(self.writeJavaScript, self.data.ifaces)

    def writeController(self, iface):
        name = self.tpl_filename % iface.name()
        info = QmlWriter.Metadata(__file__, self.parent, self.imports)
        with QmlWriter(name, self.path, info) as writer:
            writer.write(self.tpl_subitem % { 'name': iface.name() })

    def writeJavaScript(self, iface):
        enums = self.data.enumerates(iface)
        if enums:
            info = JSWriter.Metadata(__file__)
            with JSWriter(iface.name(), self.path, info) as writer:
                map(lambda e: writer.write(self.data.enum(e)), sorted(enums, key=methodcaller('name')))
