from unittest import TestCase
from unittest.mock import Mock
from adapter import Adapter
from protocol import *

class TestProtocol(TestCase):
    def test_composite_process(self):
        v = Visitor()
        c = Composite(None)
        # empty elements way
        c.load = Mock()
        c.process(v)
        c.load.assert_called_once_with()
        # not empty elements way
        i = Interface(None, None)
        i.accept = Mock()
        c.elements.append(i)
        c.process(v)
        i.accept.assert_called_once_with(v)

    def test_argument_isBasic(self):
        p = Mock()
        # basic type
        p.type = 'String'
        a = Argument(None, p)
        self.assertTrue(a.isBasic())
        # not basic type
        p.type = 'Image'
        self.assertFalse(a.isBasic())

    def test_argument_fulltype(self):
        p = Mock()
        a = Argument(None, p)
        a.interface = Mock(return_value='Common')
        # missed interface
        p.type = 'Image'
        self.assertEqual(a.fulltype(), 'Common.Image')
        # full type
        p.type = 'Common.Type1'
        self.assertEqual(a.fulltype(), 'Common.Type1')
        # error format
        p.type = 'Common.Type2.Type3'
        with self.assertRaises(RuntimeError):
            a.fulltype()
        p.type = ''
        with self.assertRaises(RuntimeError):
            a.fulltype()

    def test_argument_accept(self):
        v = Visitor()
        v.visit = Mock()
        a = Argument(None, None)
        a.accept(v)
        v.visit.assert_called_once_with(a)

    def test_enumeration_accept(self):
        v = Visitor()
        v.visit = Mock()
        e = Enumeration(None, None)
        e.accept(v)
        v.visit.assert_called_once_with(e)

    def test_protocol_load(self):
        a = Adapter()
        a.interfaces = Mock(return_value=[1, 2, 3])
        p = Protocol(a)
        p.load()
        a.interfaces.assert_called_once_with()
        self.assertEqual(len(p.elements), 3)

    def test_protocol_accept(self):
        v = Visitor()
        p = Protocol(None)
        p.process = Mock()
        # not interesting way
        v.visit = Mock(return_value=False)
        p.accept(v)
        v.visit.assert_called_once_with(p)
        # interesting way
        v.visit = Mock(return_value=True)
        p.accept(v)
        v.visit.assert_called_once_with(p)
        p.process.assert_called_once_with(v)

    def test_interface_load(self):
        a = Adapter()
        a.enumerations = Mock(return_value=[1, 2])
        s1 = Mock()
        s1.name = 'name'
        s1.interface = Mock()
        s1.interface.name = 'name'
        a.structures = Mock(return_value=[s1])
        f1 = Mock()
        f1.type = 'notification'
        f2 = Mock()
        f2.name = 'method'
        f2.type = 'request'
        f3 = Mock()
        f3.name = 'method'
        f3.type = 'response'
        a.functions = Mock(return_value=[f1, f2, f3])
        i = Interface(a, None)
        i.load()
        a.enumerations.assert_called_once_with(None)
        a.structures.assert_called_once_with(None)
        a.functions.assert_called_once_with(None)
        self.assertEqual(len(i.elements), 5)

    def test_interface_accept(self):
        v = Visitor()
        i = Interface(None, None)
        i.process = Mock()
        # not interesting way
        v.visit = Mock(return_value=False)
        i.accept(v)
        v.visit.assert_called_once_with(i)
        # interesting way
        v.visit = Mock(return_value=True)
        i.accept(v)
        v.visit.assert_called_once_with(i)
        i.process.assert_called_once_with(v)

    def test_structure_load(self):
        a = Adapter()
        p1 = Mock()
        p1.type = 'Integer'
        p2 = Mock()
        p2.type = 'Boolean'
        p3 = Mock()
        p3.type = 'Interface2.Struct2'
        a.structureParameters = Mock(return_value=[p1, p2, p3])
        i = Mock()
        i.name = 'Struct1'
        i.interface = Mock()
        i.interface.name = 'Interface1'
        Structure.structures = { 'Interface2.Struct2': None }
        s = Structure(a, i)
        s.load()
        a.structureParameters.assert_called_once_with(i)
        self.assertEqual(len(s.elements), 3)

    def test_structure_accept(self):
        v = Visitor()
        i = Mock()
        i.name = 'name'
        i.interface = Mock()
        i.interface.name = 'name'
        s = Structure(None, i)
        s.process = Mock()
        # not interesting way
        v.visit = Mock(return_value=False)
        s.accept(v)
        v.visit.assert_called_once_with(s)
        # interesting way
        v.visit = Mock(return_value=True)
        s.accept(v)
        v.visit.assert_called_once_with(s)
        s.process.assert_called_once_with(v)

    def test_signal_load(self):
        a = Adapter()
        a.functionParameters = Mock(return_value=[1, 2, 3])
        s = Signal(a, None)
        s.load()
        a.functionParameters.assert_called_once_with(None)
        self.assertEqual(len(s.elements), 3)

    def test_signal_accept(self):
        v = Visitor()
        s = Signal(None, None)
        s.process = Mock()
        # not interesting way
        v.visit = Mock(return_value=False)
        s.accept(v)
        v.visit.assert_called_once_with(s)
        # interesting way
        v.visit = Mock(return_value=True)
        s.accept(v)
        v.visit.assert_called_once_with(s)
        s.process.assert_called_once_with(v)

    def test_method_load(self):
        a = Adapter()
        a.functionParameters = Mock(side_effect=[[1, 2, 3], [4, 5]])
        m = Method(a, None, None)
        m.load()
        a.functionParameters.assert_called_with(None)
        self.assertEqual(a.functionParameters.call_count, 2)
        self.assertEqual(len(m.elements), 5)

    def test_method_accept(self):
        v = Visitor()
        m = Method(None, None, None)
        m.process = Mock()
        # not interesting way
        v.visit = Mock(return_value=False)
        m.accept(v)
        v.visit.assert_called_once_with(m)
        # interesting way
        v.visit = Mock(return_value=True)
        m.accept(v)
        v.visit.assert_called_once_with(m)
        m.process.assert_called_once_with(v)

if __name__ == '__main__':
    unittest.main()
