from unittest import TestCase
from unittest.mock import Mock, MagicMock
from MessageDescriptionVisitor import MessageDescriptionVisitor
from protocol import *

class TestMessageDescriptionVisitor(TestCase):
    def test_doTypes(self):
        msgs = MessageDescriptionVisitor('NameSpace')
        msgs.doTypes()
        self.assertEqual(msgs.type_message, 'const NameSpace::MessageDescription')
        self.assertEqual(msgs.type_structure, 'const NameSpace::StructDescription')
        self.assertEqual(msgs.type_array, 'const NameSpace::ArrayDescription')
        self.assertEqual(msgs.type_parameter, 'const NameSpace::ParameterDescription')

    def test_arrayType(self):
        msgs = MessageDescriptionVisitor('NameSpace')
        # Basic
        a = Argument(None, None)
        a.type = Mock(side_effect=['Integer', 'String', 'Boolean', 'Float'])
        self.assertEqual(msgs.arrayType(a), 'NameSpace::Integer')
        self.assertEqual(msgs.arrayType(a), 'NameSpace::String')
        self.assertEqual(msgs.arrayType(a), 'NameSpace::Boolean')
        self.assertEqual(msgs.arrayType(a), 'NameSpace::Float')
        self.assertEqual(a.type.call_count, 4)
        # Enum
        a = Argument(None, None)
        a.type = Mock(return_value='ValueEnum')
        msgs.enums = ['ValueEnum']
        self.assertEqual(msgs.arrayType(a), 'NameSpace::Enum')
        a.type.assert_called_once_with()
        # Struct
        a = Argument(None, None)
        a.type = Mock(return_value='ValueStruct')
        msgs.signatures = {'ValueStruct': 'i'}
        self.assertEqual(msgs.arrayType(a), 'NameSpace::Struct')
        a.type.assert_called_once_with()
        # Unknown
        a = Argument(None, None)
        a.type = Mock(return_value='Unkonw')
        with self.assertRaises(RuntimeError):
            msgs.arrayType(a)
        a.type.assert_called_once_with()

    def test_fulltype(self):
        msgs = MessageDescriptionVisitor('NameSpace')
        # Array
        a = Argument(None, None)
        a.isArray = Mock(return_value=True)
        self.assertEqual(msgs.fulltype(a), 'NameSpace::Array')
        a.isArray.assert_called_once_with()
        # Other
        a = Argument(None, None)
        a.isArray = Mock(return_value=False)
        msgs.arrayType = Mock(return_value='NameSpace::Float')
        self.assertNotEqual(msgs.fulltype(a), 'NameSpace::Array')
        a.isArray.assert_called_once_with()
        msgs.arrayType.assert_called_once_with(a)

    def test_arraySignature(self):
        msgs = MessageDescriptionVisitor('NameSpace')
        # Basic
        a = Argument(None, None)
        a.type = Mock(side_effect=['Integer', 'String', 'Boolean', 'Float'])
        self.assertEqual(msgs.arraySignature(a), 'i')
        self.assertEqual(msgs.arraySignature(a), 's')
        self.assertEqual(msgs.arraySignature(a), 'b')
        self.assertEqual(msgs.arraySignature(a), 'd')
        # Enum
        a = Argument(None, None)
        a.type = Mock(return_value='ValueEnum')
        msgs.enums = ['ValueEnum']
        self.assertEqual(msgs.arraySignature(a), 'i')
        a.type.assert_called_once_with()
        # Struct
        a = Argument(None, None)
        a.type = Mock(return_value='ValueStruct')
        msgs.signatures = {'ValueStruct': 'i'}
        self.assertEqual(msgs.arraySignature(a), '(i)')
        a.type.assert_called_once_with()
        # Unknown
        a = Argument(None, None)
        a.type = Mock(return_value='Unkonw')
        with self.assertRaises(RuntimeError):
            msgs.arraySignature(a)
        a.type.assert_called_once_with()

    def test_visitEnumeration(self):
        msgs = MessageDescriptionVisitor('NameSpace')
        e = Enumeration(None, None)
        e.interface = Mock(return_value='I')
        e.name = Mock(return_value='E')
        self.assertTrue(msgs.visitEnumeration(e))
        self.assertEqual(msgs.enums, ['I.E'])

    def test_visitStructure(self):
        msgs = MessageDescriptionVisitor('NameSpace')
        i = Mock()
        i.name = 'S'
        i.interface = Mock()
        i.interface.name = 'I'
        s = Structure(None, i)
        s.interface = Mock(return_value='I')
        s.name = Mock(return_value='S')
        self.assertTrue(msgs.visitStructure(s))
        self.assertEqual(msgs.names, [('I', 'S')])
        self.assertEqual(msgs.structures, {('I', 'S'): []})
        self.assertEqual(msgs.signatures, {'I.S': ''})

    def test_visitSignal(self):
        msgs = MessageDescriptionVisitor('NameSpace')
        s = Signal(None, None)
        s.interface = Mock(return_value='I')
        s.name = Mock(return_value='S')
        self.assertTrue(msgs.visitSignal(s))
        self.assertEqual(msgs.names, [('I', 'S')])
        self.assertEqual(msgs.signals, {('I', 'S'): s})
        self.assertEqual(msgs.args, {('I', 'S'): []})

    def test_visitMethod(self):
        msgs = MessageDescriptionVisitor('NameSpace')
        m = Method(None, None, None)
        m.interface = Mock(return_value='I')
        m.name = Mock(return_value='M')
        self.assertTrue(msgs.visitMethod(m))
        self.assertEqual(msgs.names, [('I', 'M')])
        self.assertEqual(msgs.methods, {('I', 'M'): m})
        self.assertEqual(msgs.args, {('I', 'M'): []})

