from unittest import TestCase
from XMLAdapter import XMLAdapter
from terms.Interface import *

class TestXMLAdapter(TestCase):
    adapter = XMLAdapter('QT_HMI_API.xml')
    def test_interfaces(self):
        common = self.adapter.interfaces()[0]
        self.assertEqual(common.name, 'Common')

    def test_interface(self):
        buttons = self.adapter.interface('Buttons')
        self.assertIsNotNone(buttons)
        self.assertEqual(buttons.name, 'Buttons')
        no_found = self.adapter.interface('ErrorName')
        self.assertIsNone(no_found)

    def test_functions(self):
        buttons = Interface()
        buttons.name = 'Buttons'
        get_cap = self.adapter.functions(buttons)[0]
        self.assertEqual(get_cap.name, 'GetCapabilities')

    def test_function(self):
        buttons = Interface()
        buttons.name = 'Buttons'
        on_event = self.adapter.function('OnButtonEvent', buttons)
        self.assertIsNotNone(on_event)
        self.assertEqual(on_event.name, 'OnButtonEvent')
        self.assertEqual(on_event.type, 'response')
        no_found = self.adapter.function('ErrorName', buttons)
        self.assertIsNone(no_found)

    def test_structures(self):
        common = Interface()
        common.name = 'Common'
        msg = self.adapter.structures(common)[0]
        self.assertEqual(msg.name, 'UserFriendlyMessage')

    def test_structure(self):
        common = Interface()
        common.name = 'Common'
        msg = self.adapter.structure('UserFriendlyMessage', common)
        self.assertIsNotNone(msg)
        self.assertEqual(msg.name, 'UserFriendlyMessage')
        no_found = self.adapter.structure('ErrorName', common)
        self.assertIsNone(no_found)

    def test_enumerations(self):
        common = Interface()
        common.name = 'Common'
        ret = self.adapter.enumerations(common)[0]
        self.assertEqual(ret.name, 'Result')
        self.assertEqual(len(ret.elements), 25)
        self.assertEqual(ret.elements[0].name, 'SUCCESS')
        self.assertEqual(ret.elements[0].value, 0)

    def test_enumeration(self):
        common = Interface()
        common.name = 'Common'
        event = self.adapter.enumeration('ButtonEventMode', common)
        self.assertIsNotNone(event)
        self.assertEqual(event.name, 'ButtonEventMode')
        self.assertEqual(len(event.elements), 2)
        self.assertEqual(event.elements[0].name, 'BUTTONUP')
        self.assertEqual(event.elements[1].name, 'BUTTONDOWN')
        no_found = self.adapter.enumeration('ErrorName', common)
        self.assertIsNone(no_found)

if __name__ == '__main__':
    unittest.main()
