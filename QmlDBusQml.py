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
        map(self.writeController, self.data.interfaces())
        map(self.writeJavaScript, self.data.interfaces())

    def writeController(self, interface):
        methods = self.data.methods(interface)
        signals = self.data.signals(interface)
        if signals or methods:
            name = self.tpl_filename % interface
            info = QmlWriter.Metadata(__file__, self.parent, self.imports)
            with QmlWriter(name, self.path, info) as writer:
                writer.write(self.tpl_subitem % { 'name': interface })
                map(lambda m: writer.write(self.data.method(m)), methods)
                map(lambda s: writer.write(self.data.signal(s)), signals)

    def writeJavaScript(self, interface):
        enums = self.data.enumerates(interface)
        if enums:
            info = JSWriter.Metadata(__file__)
            with JSWriter(interface, self.path, info) as writer:
                map(lambda e: writer.write(self.data.enum(e)),
                    sorted(enums, key=methodcaller('name')))
