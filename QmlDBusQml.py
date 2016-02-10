from __future__ import print_function
import os
from datetime import date
from saver import Saver
from header import CppWarning
from header import CppHeader

class QmlDBusQml(Saver):
    generator = os.path.basename(__file__)
    tpl_filename = '%sProxy.qml'

    def __init__(self, data, version="5.1.0"):
        self.data = data

    def write(self, path):
        self.path = path
        map(self.writeController, self.data.ifaces)

    def writeController(self, iface):
        fd = open(os.path.join(self.path, self.tpl_filename % iface.name()), 'w')
        os.sys.stdout = fd
        print(CppWarning % self.generator)
        print(CppHeader % date.today().year)
        fd.close() 
