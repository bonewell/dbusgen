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
#        msgs.arraySignature()

    def test_visitEnumeration(self):
        msgs = MessageDescriptionVisitor('NameSpace')
