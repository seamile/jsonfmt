import os
import unittest
from json import load as j_load
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element

from jsonfmt.xml2py import XmlElement, dumps, loads


class TestXmlElement(unittest.TestCase):

    def setUp(self) -> None:
        dirpath = os.path.dirname(__file__)

        jsonfile = os.path.join(dirpath, 'example.json')
        with open(jsonfile) as j_fp:
            self.pyobj = j_load(j_fp)

        xmlfile = os.path.join(dirpath, 'example.xml')
        with open(xmlfile) as x_fp:
            self.xml = x_fp.read()

    def test_init(self):
        ele = XmlElement('test', {'attr1': 'value1'}, 'text content', 'tail text')
        self.assertEqual(ele.tag, 'test')
        self.assertEqual(ele.attrib, {'attr1': 'value1'})
        self.assertEqual(ele.text, 'text content')
        self.assertEqual(ele.tail, 'tail text')

    def test_makeelement(self):
        ele = XmlElement.makeelement('tag', {'attr': 'val'})
        self.assertIsInstance(ele, XmlElement)
        self.assertEqual(ele.tag, 'tag')
        self.assertEqual(ele.attrib, {'attr': 'val'})

    def test_clone(self):
        src = Element('src')
        src.attrib['attr'] = 'value'
        src.text = 'text'
        child = Element('child')
        src.append(child)

        cloned = XmlElement.clone(src)
        self.assertIsInstance(cloned, XmlElement)
        self.assertEqual(cloned.tag, 'src')
        self.assertEqual(cloned.attrib, {'attr': 'value'})
        self.assertEqual(cloned.text, 'text')
        self.assertTrue(len(cloned), 1)
        self.assertEqual(cloned[0].tag, 'child')

    def test_from_xml(self):
        xml = '<root><item attr="value">Text</item></root>'
        ele = XmlElement.from_xml(xml)
        self.assertIsInstance(ele, XmlElement)
        self.assertEqual(ele.tag, 'root')
        self.assertEqual(len(ele), 1)
        self.assertEqual(ele[0].tag, 'item')
        self.assertEqual(ele[0].attrib, {'attr': 'value'})
        self.assertEqual(ele[0].text, 'Text')

    def test_to_xml_minimal(self):
        ele = XmlElement('root')
        ele.spawn('item', {'attr': 'value'}, 'Text')
        xml = ele.to_xml(minimal=True)
        self.assertIn('<item attr="value">Text</item>', xml)

    def test_to_xml_pretty(self):
        ele = XmlElement('root')
        ele.spawn('item', {'k': 'val'})
        xml1 = ele.to_xml(indent=2)
        self.assertIn('<root>\n  <item k="val"/>\n</root>', xml1)
        xml2 = ele.to_xml(minimal=True)
        self.assertIn('<root><item k="val" /></root>', xml2)

    def test_spawn(self):
        parent = XmlElement('parent')
        child = parent.spawn('child', {'attr': 'value'}, 'Text')
        self.assertIsInstance(child, XmlElement)
        self.assertEqual(child.tag, 'child')
        self.assertEqual(child.attrib, {'attr': 'value'})
        self.assertEqual(child.text, 'Text')
        self.assertIs(child.parent, parent)

    def test_get_attrs(self):
        ele = XmlElement('ele', {'attr1': '1', 'attr2': '2'}, '3')
        ele.spawn('sub_ele', {'attr3': '3'})
        attrs = ele._get_attrs()
        self.assertEqual(attrs,
                         {'@attr1': 1, '@attr2': 2, '@text': 3, 'sub_ele': {'@attr3': 3}})

    def test_from_py(self):
        obj1 = {'foo': [1, 2, 3]}
        ele1 = XmlElement.from_py(obj1)
        self.assertEqual(ele1.tag, 'root')
        self.assertEqual(len(ele1), 3)
        self.assertEqual(ele1[0].text, '1')
        self.assertEqual(ele1[1].text, '2')
        self.assertEqual(ele1[2].text, '3')

        obj2 = [
            [1, 2, 3],
            {
                '@attr': 'value',
                '@text': 'hello world',
                'item': [
                    {'@sub_attr': 'sub_value1'},
                    {'name': 'space'}
                ]
            }
        ]

        xml = (
            '<?xml version="1.0" ?>\n'
            '<root>\n'
            '  <root>[1, 2, 3]</root>\n'
            '  <root attr="value">\n'
            '    hello world\n'
            '    <item sub_attr="sub_value1"/>\n'
            '    <item>\n'
            '      <name>space</name>\n'
            '    </item>\n'
            '  </root>\n'
            '</root>\n'
        )

        ele2 = XmlElement.from_py(obj2)
        self.assertEqual(ele2.to_xml(indent=2), xml)

    def test_to_py(self):
        ele = XmlElement('root', {'attr': 'value'})
        ele.spawn('item', {'red': 'red'}, '[1,2,3]')
        py_obj = ele.to_py()
        self.assertEqual(py_obj,
                         {'@attr': 'value', 'item': {'@red': 'red', '@text': [1, 2, 3]}})

    def test_loads(self):
        xml = '<root><item k="v" x="y"><l>1</l><l>2</l><l>3</l></item></root>'
        py_obj = loads(xml)
        self.assertEqual(py_obj, {'item': {'@k': 'v', '@x': 'y', 'l': [1, 2, 3]}})
        self.assertEqual(loads(self.xml), self.pyobj)

    def test_dumps(self):
        obj = {'root': {'item': [{'@sub_attr': 'sub_value1'}, {'@sub_attr': 'sub_value2'}]}}
        xml = dumps(obj, indent='  ', sort_keys=True)
        parsed_xml = parseString(xml)
        self.assertIsNotNone(parsed_xml.documentElement)
        self.assertEqual(parsed_xml.documentElement.tagName, 'root')
        items = parsed_xml.getElementsByTagName('item')
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].getAttribute('sub_attr'), 'sub_value1')
        self.assertEqual(items[1].getAttribute('sub_attr'), 'sub_value2')

        self.assertEqual(dumps(self.pyobj, '2'), self.xml)


if __name__ == "__main__":
    unittest.main()
