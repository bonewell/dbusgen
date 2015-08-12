from unittest import TestCase
from unittest.mock import Mock
from terms.Adapter import Adapter
from protocol.Composite import Composite
from protocol.Interface import Interface
from protocol.Argument import Argument
from protocol.Enumeration import Enumeration
from protocol.Structure import Structure
from protocol.Method import Method
from protocol.Signal import Signal
from protocol.Protocol import Protocol

from protocol.Visitor import Visitor

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
        a.structures = Mock(return_value=[1])
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
        a.parameters = Mock(return_value=[1, 2, 3])
        s = Structure(a, None)
        s.load()
        a.parameters.assert_called_once_with(None)
        self.assertEqual(len(s.elements), 3)

    def test_structure_accept(self):
        v = Visitor()
        s = Structure(None, None)
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
        a.parameters = Mock(return_value=[1, 2, 3])
        s = Signal(a, None)
        s.load()
        a.parameters.assert_called_once_with(None)
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
        a.parameters = Mock(side_effect=[[1, 2, 3], [4, 5]])
        m = Method(a, None, None)
        m.load()
        a.parameters.assert_called_with(None)
        self.assertEqual(a.parameters.call_count, 2)
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
