from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import MagicMock
from xml.etree import ElementTree
from DBusIntrospectionVisitor import DBusIntrospectionVisitor
from protocol.Argument import Argument
from protocol.Argument import TypeArgument
from protocol.Structure import Structure
from protocol.Enumeration import Enumeration
from protocol.Signal import Signal
from protocol.Method import Method
from protocol.Interface import Interface

class TestDBusIntrospectionVisitor(TestCase):
    def test_xml(self):
        dbus = DBusIntrospectionVisitor('sdl', 'com.sdl', '/com/sdl')
        dbus.doctype = 'doctype'
        # full xml
        dbus.tree = Mock() 
        ElementTree.tostring = Mock(return_value=' and xml of all')
        self.assertEqual(dbus.xml(), 'doctype\n and xml of all')
        # interface exist
        ElementTree.tostring = Mock(return_value=' and xml of VR')
        tree = Mock()
        dbus.tree.find = Mock(return_value=Mock())
        xml = dbus.xml('VR')
        dbus.tree.find.assert_called_once_with("interface[@name='com.sdl.sdl.VR']")
        self.assertEqual(xml, 'doctype\n and xml of VR')
        # unknown interface
        dbus.tree.find = Mock(return_value=None)
        with self.assertRaises(RuntimeError):
            xml = dbus.xml('TTS')
        dbus.tree.find.assert_called_once_with("interface[@name='com.sdl.sdl.TTS']")

    def test_signature(self):
        dbus = DBusIntrospectionVisitor(None, None, None)
        a = Argument(None, None)
        # mandatory Integer
        a.type = Mock(return_value='Integer')
        a.isArray = Mock(return_value=False)
        a.isMandatory = Mock(return_value=True)
        self.assertEqual(dbus.signature(a), 'i')
        a.isArray.assert_called_once_with()
        a.isMandatory.assert_called_once_with()
        # mandatory String
        a.type = Mock(return_value='String')
        a.isArray = Mock(return_value=False)
        a.isMandatory = Mock(return_value=True)
        self.assertEqual(dbus.signature(a), 's')
        a.isArray.assert_called_once_with()
        a.isMandatory.assert_called_once_with()
        # mandatory Boolean
        a.type = Mock(return_value='Boolean')
        a.isArray = Mock(return_value=False)
        a.isMandatory = Mock(return_value=True)
        self.assertEqual(dbus.signature(a), 'b')
        a.isArray.assert_called_once_with()
        a.isMandatory.assert_called_once_with()
        # mandatory Float
        a.type = Mock(return_value='Float')
        a.isArray = Mock(return_value=False)
        a.isMandatory = Mock(return_value=True)
        self.assertEqual(dbus.signature(a), 'd')
        a.isArray.assert_called_once_with()
        a.isMandatory.assert_called_once_with()
        # not mandatory Float
        a.type = Mock(return_value='Float')
        a.isArray = Mock(return_value=False)
        a.isMandatory = Mock(return_value=False)
        self.assertEqual(dbus.signature(a), '(bd)')
        a.isArray.assert_called_once_with()
        a.isMandatory.assert_called_once_with()
        # array of Float
        a.type = Mock(return_value='Float')
        a.isArray = Mock(return_value=True)
        a.isMandatory = Mock(return_value=True)
        self.assertEqual(dbus.signature(a), 'ad')
        a.isArray.assert_called_once_with()
        a.isMandatory.assert_called_once_with()
        # Enumeration
        dbus.enums.append('Common.Type')
        a.type = Mock(return_value='Common.Type')
        a.isArray = Mock(return_value=False)
        a.isMandatory = Mock(return_value=True)
        self.assertEqual(dbus.signature(a), 'i')
        a.isArray.assert_called_once_with()
        a.isMandatory.assert_called_once_with()
        # Structure
        dbus.structs['Common.Image'] = 'bis'
        a.type = Mock(return_value='Common.Image')
        a.isArray = Mock(return_value=False)
        a.isMandatory = Mock(return_value=True)
        self.assertEqual(dbus.signature(a), '(bis)')
        a.isArray.assert_called_once_with()
        a.isMandatory.assert_called_once_with()
        # unknown type
        a.type = Mock(return_value='What?')
        a.isArray = Mock(return_value=False)
        a.isMandatory = Mock(return_value=True)
        with self.assertRaises(RuntimeError):
            dbus.signature(a)
        self.assertEqual(a.isArray.call_count, 0)
        self.assertEqual(a.isMandatory.call_count, 0)

    def test_prepareStruct(self):
        dbus = DBusIntrospectionVisitor(None, None, None)
        dbus.signature = Mock(return_value='bis')
        a = Argument(None, None)
        a.interface = Mock(return_value='I')
        a.parent = Mock(return_value='P')
        dbus.structs['I.P'] = ''
        dbus.prepareStruct(a)
        dbus.signature.assert_called_once_with(a)
        self.assertEqual(len(dbus.structs), 1)
        self.assertEqual(dbus.structs['I.P'], 'bis')

    def test_createArgument(self):
        dbus = DBusIntrospectionVisitor(None, None, None)
        a = Argument(None, None)
        # Input
        dbus.parent = []
        dbus.signature = Mock(return_value='b')
        a.name = Mock(return_value='Param')
        a.direction = TypeArgument.Input
        dbus.createArgument(a)
        a.name.assert_called_once_with()
        dbus.signature.assert_called_once_with(a)
        self.assertEqual(ElementTree.tostring(dbus.parent[0]),
        b'<arg direction="in" name="Param" type="b" />')
        # Output
        dbus.parent = []
        dbus.signature = Mock(return_value='b')
        a.name = Mock(return_value='Param')
        a.direction = TypeArgument.Output
        dbus.createArgument(a)
        a.name.assert_called_once_with()
        dbus.signature.assert_called_once_with(a)
        self.assertEqual(ElementTree.tostring(dbus.parent[0]),
        b'<arg direction="out" name="Param" type="b" />')
        # Undefined
        dbus.parent = []
        dbus.signature = Mock(return_value='b')
        a.name = Mock(return_value='Param')
        a.direction = TypeArgument.Undefined
        dbus.createArgument(a)
        a.name.assert_called_once_with()
        dbus.signature.assert_called_once_with(a)
        self.assertEqual(ElementTree.tostring(dbus.parent[0]),
        b'<arg name="Param" type="b" />')

    def test_appendInterface(self):
        dbus = DBusIntrospectionVisitor(None, None, None)
        dbus.iface = None
        # success append
        dbus.empty_iface = True
        dbus.tree = Mock()
        dbus.tree.append = Mock()
        dbus.appendInterface()
        dbus.tree.append.assert_called_once_with(dbus.iface)
        self.assertFalse(dbus.empty_iface)
        # don't need to append
        dbus.tree.append = Mock()
        dbus.appendInterface()
        self.assertFalse(dbus.empty_iface)
        self.assertFalse(dbus.tree.append.called)

    def test_visitProtocol(self):
        dbus = DBusIntrospectionVisitor(None, None, None)
        self.assertTrue(dbus.visitProtocol(None))

    def test_visitInterface(self):
        dbus = DBusIntrospectionVisitor('sdl', 'com.sdl', None)
        dbus.empty_iface = False
        i = Interface(None, None)
        i.name = Mock(return_value='I')
        self.assertTrue(dbus.visitInterface(i))
        i.name.assert_called_with()
        self.assertTrue(dbus.empty_iface)
        self.assertEqual(ElementTree.tostring(dbus.iface),
        b'<interface name="com.sdl.sdl.I" />')

    def test_visitEnumeration(self):
        dbus = DBusIntrospectionVisitor(None, None, None)
        dbus.enums = []
        e = Enumeration(None, None)
        e.interface = Mock(return_value='I')
        e.name = Mock(return_value='En')
        dbus.visitEnumeration(e)
        e.interface.assert_called_once_with()
        e.name.assert_called_once_with()
        self.assertEqual(len(dbus.enums), 1)
        self.assertEqual(dbus.enums[0], 'I.En')

    def test_visitStructure(self):
        dbus = DBusIntrospectionVisitor(None, None, None)
        dbus.structs = {}
        s = Structure(None, None)
        s.interface = Mock(return_value='I')
        s.name = Mock(return_value='St')
        self.assertTrue(dbus.visitStructure(s))
        s.interface.assert_called_once_with()
        s.name.assert_called_once_with()
        self.assertEqual(len(dbus.structs), 1)
        self.assertEqual(dbus.structs['I.St'], '')

    def test_visitSignal(self):
        dbus = DBusIntrospectionVisitor('sdl', None, None)
        dbus.appendInterface = Mock()
        s = Signal(None, None)
        s.name = Mock(return_value='S')
        # not interesting signal
        s.provider = Mock(return_value='hmi')
        self.assertFalse(dbus.visitSignal(s))
        s.provider.assert_called_once_with()
        # interesting signal
        dbus.iface = Mock()
        dbus.iface.append = Mock()
        s.provider = Mock(return_value='sdl')
        self.assertTrue(dbus.visitSignal(s))
        s.provider.assert_called_once_with()
        s.name.assert_called_with()
        dbus.appendInterface.assert_called_once_with()
        dbus.iface.append.assert_called_once_with(dbus.parent)
        self.assertEqual(ElementTree.tostring(dbus.parent), b'<signal name="S" />')

    def test_visitMethod(self):
        dbus = DBusIntrospectionVisitor('sdl', None, None)
        dbus.appendInterface = Mock()
        m = Method(None, None, None)
        m.name = Mock(return_value='M')
        # not interesting signal
        m.provider = Mock(return_value='hmi')
        self.assertFalse(dbus.visitMethod(m))
        m.provider.assert_called_once_with()
        # interesting signal
        dbus.iface = Mock()
        dbus.iface.append = Mock()
        m.provider = Mock(return_value='sdl')
        self.assertTrue(dbus.visitMethod(m))
        m.provider.assert_called_once_with()
        m.name.assert_called_with()
        dbus.appendInterface.assert_called_once_with()
        dbus.iface.append.assert_called_once_with(dbus.parent)
        self.assertEqual(ElementTree.tostring(dbus.parent),
        b'<method name="M"><arg direction="out" name="retCode" type="i" /></method>')

    def test_visitArgument(self):
        dbus = DBusIntrospectionVisitor(None, None, None)
        dbus.prepareStruct = Mock()
        dbus.createArgument = Mock()
        a = Argument(None, None)
        a.name = Mock(return_value='Name')
        # argument is contained in Structure
        a.isStruct = Mock(return_value=True)
        dbus.visitArgument(a)
        a.isStruct.assert_called_once_with()
        dbus.prepareStruct.assert_called_once_with(a)
        # argument is contained in Signal or Method
        a.isStruct = Mock(return_value=False)
        dbus.visitArgument(a)
        a.isStruct.assert_called_once_with()
        dbus.createArgument.assert_called_once_with(a)

    def test_visit(self):
        self.maxDiff = None
        dbus = DBusIntrospectionVisitor('sdl', 'com.sdl', '/com/sdl')
        dbus.visitProtocol(None)
        i = Interface(None, None)
        i.name = Mock(return_value='I')
        dbus.visitInterface(i)
        e = Enumeration(None, None)
        e.name = Mock(return_value='E')
        e.interface = Mock(return_value='I')
        dbus.visitEnumeration(e)
        s = Structure(None, None)
        s.name = Mock(return_value='S')
        s.interface = Mock(return_value='I')
        dbus.visitStructure(s)
        a01 = Argument(None, None)
        a01.name = Mock(return_value='a01')
        a01.isStruct = Mock(return_value=True)
        a01.interface = Mock(return_value='I')
        a01.parent = Mock(return_value='S')
        a01.type = Mock(return_value='Float')
        a01.isArray = Mock(return_value=False)
        a01.isMandatory = Mock(return_value=True)
        dbus.visitArgument(a01)
        a02 = Argument(None, None)
        a02.name = Mock(return_value='a02')
        a02.isStruct = Mock(return_value=True)
        a02.interface = Mock(return_value='I')
        a02.parent = Mock(return_value='S')
        a02.type = Mock(return_value='String')
        a02.isArray = Mock(return_value=False)
        a02.isMandatory = Mock(return_value=True)
        dbus.visitArgument(a02)
        s = Signal(None, None)
        s.name = Mock(return_value='S')
        s.provider = Mock(return_value='sdl')
        dbus.visitSignal(s)
        a1 = Argument(None, None)
        a1.name = Mock(return_value='arg1')
        a1.type = Mock(return_value='String')
        a1.isStruct = Mock(return_value=False)
        a1.isArray = Mock(return_value=False)
        a1.isMandatory = Mock(return_value=True)
        dbus.visitArgument(a1)
        a2 = Argument(None, None)
        a2.name = Mock(return_value='arg2')
        a2.type = Mock(return_value='I.E')
        a2.isStruct = Mock(return_value=False)
        a2.isArray = Mock(return_value=True)
        a2.isMandatory = Mock(return_value=True)
        dbus.visitArgument(a2)
        m = Method(None, None, None)
        m.name = Mock(return_value='M')
        m.provider = Mock(return_value='sdl')
        dbus.visitMethod(m)
        a3 = Argument(None, None, TypeArgument.Input)
        a3.name = Mock(return_value='arg3')
        a3.type = Mock(return_value='I.S')
        a3.isStruct = Mock(return_value=False)
        a3.isArray = Mock(return_value=False)
        a3.isMandatory = Mock(return_value=False)
        dbus.visitArgument(a3)
        doctype = ('<!DOCTYPE node PUBLIC "-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"'
        +' "http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">')
        xml = (b'<node name="/com/sdl"><interface name="com.sdl.sdl.I"><signal name="S">'
        + b'<arg name="arg1" type="s" /><arg name="arg2" type="ai" /></signal><method name="M">'
        + b'<arg direction="out" name="retCode" type="i" /><arg direction="in" name="arg3" type="(b(ds))" />'
        + b'</method></interface></node>')
        expect = '%s\n%s' % (doctype, xml)
        self.assertEqual(dbus.xml(), expect) 
