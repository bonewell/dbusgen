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
        no_found = self.adapter.function('ErrorName', buttons)
        self.assertIsNone(no_found)

if __name__ == '__main__':
    unittest.main()
