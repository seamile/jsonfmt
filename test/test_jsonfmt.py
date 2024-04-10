import json
import os
import sys
import tempfile
import unittest
from argparse import Namespace
from contextlib import contextmanager
from copy import deepcopy
from functools import partial
from io import StringIO
from unittest.mock import patch

import pyperclip
from jmespath import compile as jcompile
from jsonpath_ng import parse as jparse
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, TOMLLexer, XmlLexer, YamlLexer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from jsonfmt import jsonfmt

JSON_FILE = f'{BASE_DIR}/test/example.json'
with open(JSON_FILE) as json_fp:
    JSON_TEXT = json_fp.read()

TOML_FILE = f'{BASE_DIR}/test/example.toml'
with open(TOML_FILE) as toml_fp:
    TOML_TEXT = toml_fp.read()

XML_FILE = f'{BASE_DIR}/test/example.xml'
with open(XML_FILE) as xml_fp:
    XML_TEXT = xml_fp.read()

YAML_FILE = f'{BASE_DIR}/test/example.yaml'
with open(YAML_FILE) as yaml_fp:
    YAML_TEXT = yaml_fp.read()


def color(text, fmt):
    functions = {
        'json': partial(highlight, lexer=JsonLexer(), formatter=TerminalFormatter()),
        'toml': partial(highlight, lexer=TOMLLexer(), formatter=TerminalFormatter()),
        'xml': partial(highlight, lexer=XmlLexer(), formatter=TerminalFormatter()),
        'yaml': partial(highlight, lexer=YamlLexer(), formatter=TerminalFormatter()),
    }
    fn = functions[fmt]
    return fn(text)


class FakeStream(StringIO):

    def __init__(self, initial_value='', newline='\n', tty=True):
        super().__init__(initial_value, newline)
        self._istty = tty

    def isatty(self):
        return self._istty

    def read(self):
        self.seek(0)
        content = super().read()

        self.seek(0)
        self.truncate()
        return content


class StdIn(FakeStream):
    name = '<stdin>'

    def fileno(self) -> int:
        return 0


class StdOut(FakeStream):
    name = '<stdout>'

    def fileno(self) -> int:
        return 1


class StdErr(FakeStream):
    name = '<stderr>'

    def fileno(self) -> int:
        return 2


class JSONFormatToolTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.py_obj = json.loads(JSON_TEXT)

    @contextmanager
    def assertNotRaises(self, exc_type):
        try:
            yield None
        except exc_type:
            raise self.failureException('{} raised'.format(exc_type.__name__))

    def test_is_clipboard_available(self):
        available = jsonfmt.is_clipboard_available()
        self.assertIsInstance(available, bool)

    def test_parse_querypath(self):
        jmespath, jsonpath = 'actions.name', '$..name'
        # test parse jmespath
        res1 = jsonfmt.parse_querypath(jmespath, None)
        res2 = jsonfmt.parse_querypath(jmespath, 'jmespath')

        self.assertEqual(res1, res2)
        # test parse jsonpath
        res3 = jsonfmt.parse_querypath(jsonpath, None)
        res4 = jsonfmt.parse_querypath(jsonpath, 'jsonpath')
        self.assertEqual(res3, res4)

        # test wrong args
        self.assertEqual(jsonfmt.parse_querypath(None, None), None)
        with self.assertRaises(SystemExit):
            jsonfmt.parse_querypath('as*df', None)

        with self.assertRaises(SystemExit):
            jsonfmt.parse_querypath(jsonpath, 'wrong')

    def test_parse_to_pyobj_with_jmespath(self):
        # normal parameters test
        matched_obj = jsonfmt.parse_to_pyobj(JSON_TEXT, jcompile("actions[:].calorie"))
        self.assertEqual(matched_obj, ([1294.9, -2375, -420.5], 'json'))
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, jcompile("actions[*].name"))
        self.assertEqual(matched_obj, (['eating', 'sporting', 'sleeping'], 'toml'))
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jcompile("actions[*].date"))
        self.assertEqual(matched_obj, (['2021-03-02', '2023-04-27', '2023-05-15'], 'yaml'))
        # test not exists key
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, jcompile("not_exist_key"))
        self.assertEqual(matched_obj, (None, 'toml'))
        # test index out of range
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jcompile('actions[7]'))
        self.assertEqual(matched_obj, (None, 'yaml'))

    def test_parse_to_pyobj_with_jsonpath(self):
        # normal parameters test
        matched_obj = jsonfmt.parse_to_pyobj(JSON_TEXT, jparse("age"))
        self.assertEqual(matched_obj, (23, 'json'))
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, jparse("$..name"))
        self.assertEqual(matched_obj, (['Bob', 'eating', 'sporting', 'sleeping'], 'toml'))
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jparse("actions[*].date"))
        self.assertEqual(matched_obj, (['2021-03-02', '2023-04-27', '2023-05-15'], 'yaml'))
        # test not exists key
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, jparse("not_exist_key"))
        self.assertEqual(matched_obj, (None, 'toml'))
        # test index out of range
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jparse('actions[7]'))
        self.assertEqual(matched_obj, (None, 'yaml'))

    def test_parse_to_pyobj_with_wrong_fmt(self):
        with self.assertRaises(jsonfmt.FormatError), open(__file__) as fp:
            jsonfmt.parse_to_pyobj(fp.read(), jcompile("actions[0].calorie"))

    def test_modify_pyobj_for_adding(self):
        # test empty sets and pops
        obj = deepcopy(self.py_obj)
        jsonfmt.modify_pyobj(obj, [], [])
        self.assertEqual(obj, self.py_obj)

        # test add new value
        obj = deepcopy(self.py_obj)
        # add single value to dict
        jsonfmt.modify_pyobj(obj, ['new=value'], [])
        self.assertEqual(obj['new'], 'value')
        # add single value to list
        jsonfmt.modify_pyobj(obj, ['actions[10]={"A":"B"}'], [])
        self.assertEqual(obj['actions'][-1], {"A": "B"})
        # add multiple values at once
        jsonfmt.modify_pyobj(obj, ['new=[1,2,3]', 'actions[11]={"X":"Y"}'], [])
        self.assertEqual(obj['new'], [1, 2, 3])
        self.assertEqual(obj['actions'][-1], {"X": "Y"})

    def test_modify_pyobj_for_modifying(self):
        # test modify values
        obj = deepcopy(self.py_obj)
        # modify single value
        jsonfmt.modify_pyobj(obj, ['name=Alex'], [])
        self.assertEqual(obj['name'], 'Alex')
        # add multiple values at once
        jsonfmt.modify_pyobj(obj, ['gender=[male]', 'actions[0].calorie=0'], [])
        self.assertEqual(obj['gender'], '[male]')
        self.assertEqual(obj['actions'][0]['calorie'], 0)

    def test_modify_pyobj_for_popping(self):
        # test pop values
        obj = deepcopy(self.py_obj)
        n_actions = len(obj['actions'])
        # pop single value
        jsonfmt.modify_pyobj(obj, [], ['age'])
        self.assertNotIn('age', obj)
        # pop multiple values at once
        jsonfmt.modify_pyobj(obj, [], ['money', 'actions[1]', 'actions.0.date'])
        self.assertNotIn('money', obj)
        self.assertNotIn('date', obj['actions'][0])
        self.assertEqual(n_actions - 1, len(obj['actions']))

    def test_modify_pyobj_for_all(self):
        # test adding, popping and modifying simultaneously
        obj = deepcopy(self.py_obj)
        jsonfmt.modify_pyobj(obj,
                             ['new=abc', 'actions.0=[]'],  # add and modify
                             ['actions.1.name', 'age'])  # pop
        self.assertEqual(obj['new'], 'abc')
        self.assertEqual(obj['actions'][0], [])
        self.assertNotIn('name', obj['actions'][1])
        self.assertNotIn('age', obj)

        # test exceptions
        obj = deepcopy(self.py_obj)
        with patch('sys.stderr', StdErr()):
            # modifying
            jsonfmt.modify_pyobj(obj, ['aa.bb=empty'], [])
            self.assertIn('invalid key path', sys.stderr.read())
            # popping
            jsonfmt.modify_pyobj(obj, [], ['actions[3]'])
            self.assertIn('invalid key path', sys.stderr.read())

    def test_get_overview(self):
        # test dict obj
        obj = deepcopy(self.py_obj)
        obj['dict'] = {"a": 7758, "b": [1, 2, 3]}
        expected_1 = {
            'actions': [],
            'age': 23,
            'gender': '...',
            'money': 3.1415926,
            'name': '...',
            'dict': {
                'a': 7758,
                'b': []
            }
        }
        overview = jsonfmt.get_overview(obj)
        self.assertEqual(overview, expected_1)

        # test list obj
        obj = deepcopy(self.py_obj['actions'])
        expected_2 = [
            {
                "name": "...",
                "calorie": 1294.9,
                "date": "..."
            }
        ]
        overview = jsonfmt.get_overview(obj)
        self.assertEqual(overview, expected_2)

    def test_format_to_text(self):
        py_obj = {"name": "约翰", "age": 30}
        # format to json (compacted)
        j_compacted = jsonfmt.format_to_text(py_obj, 'json',
                                             compact=True, escape=True,
                                             indent='4', sort_keys=False)
        self.assertEqual(j_compacted.strip(), '{"name":"\\u7ea6\\u7ff0","age":30}')

        # format to json (indentation)
        j_indented = jsonfmt.format_to_text(py_obj, 'json',
                                            compact=False, escape=False,
                                            indent='t', sort_keys=True)
        self.assertEqual(j_indented.strip(), '{\n\t"age": 30,\n\t"name": "约翰"\n}')

        # format to toml
        toml_text = jsonfmt.format_to_text(self.py_obj, 'toml',
                                           compact=False, escape=False,
                                           indent='4', sort_keys=False)
        self.assertEqual(toml_text.strip(), TOML_TEXT.strip())

        # format to xml
        xml_text = jsonfmt.format_to_text(py_obj, 'xml',
                                          compact=True, escape=False,
                                          indent='t', sort_keys=True)
        result = '<root><age>30</age><name>约翰</name></root>'
        self.assertEqual(xml_text.strip(), result)

        # format to yaml
        yaml_text = jsonfmt.format_to_text(self.py_obj, 'yaml',
                                           compact=False, escape=False,
                                           indent='2', sort_keys=False)
        self.assertEqual(yaml_text.strip(), YAML_TEXT.strip())

        # test exceptions
        with self.assertRaises(jsonfmt.FormatError):
            jsonfmt.format_to_text([1, 2, 3], 'toml',
                                   compact=False, escape=False,
                                   indent='4', sort_keys=False)

        with self.assertRaises(jsonfmt.FormatError):
            jsonfmt.format_to_text(py_obj, 'unknow',
                                   compact=False, escape=False,
                                   indent='4', sort_keys=False)

    def test_output(self):
        # output JSON to clipboard
        jsonfmt.TEMP_CLIPBOARD.seek(0)
        jsonfmt.TEMP_CLIPBOARD.truncate()
        jsonfmt.output(jsonfmt.TEMP_CLIPBOARD, JSON_TEXT, 'json')
        jsonfmt.output(jsonfmt.TEMP_CLIPBOARD, XML_TEXT, 'xml')
        jsonfmt.TEMP_CLIPBOARD.seek(0)
        self.assertEqual(jsonfmt.TEMP_CLIPBOARD.read(),
                         JSON_TEXT + '\n\n' + XML_TEXT)

        # output TOML to file (temp file)
        with tempfile.NamedTemporaryFile(mode='r+') as tmpfile:
            jsonfmt.output(tmpfile, TOML_TEXT, 'toml')
            tmpfile.seek(0)
            self.assertEqual(tmpfile.read(), TOML_TEXT)

        # output YAML to stdout (mock)
        with patch('sys.stdout', StdOut()):
            jsonfmt.output(sys.stdout, YAML_TEXT, 'yaml')
            self.assertEqual(sys.stdout.read(), color(YAML_TEXT, 'yaml'))

        # output unknow format
        with self.assertRaises(KeyError), patch('sys.stdout', StdOut()):
            jsonfmt.output(sys.stdout, YAML_TEXT, 'null')

    def test_parse_cmdline_args(self):
        # test default parameters
        default_args = Namespace(
            cp2clip=False,
            diff=False,
            difftool=None,
            overview=False,
            overwrite=False,
            compact=False,
            escape=False,
            format=None,
            indent='2',
            querylang=None,
            querypath=None,
            sort_keys=False,
            set=None,
            pop=None,
            files=[]
        )

        with patch('sys.argv', ['jf']):
            actual_args = jsonfmt.parse_cmdline_args().parse_args()
            self.assertEqual(actual_args, default_args)

        # test specified parameters
        expected_args = Namespace(
            cp2clip=False,
            diff=True,
            difftool=None,
            overview=False,
            overwrite=False,
            compact=True,
            escape=True,
            format='toml',
            indent='4',
            querylang='jsonpath',
            querypath='path.to.json',
            sort_keys=True,
            set='a; b',
            pop='c; d',
            files=['file1.json', 'file2.json']
        )
        with patch('sys.argv', ['jf', '-d', '-c', '-e', '-f', 'toml', '-i', '4',
                                '-l', 'jsonpath', '-p', 'path.to.json', '-s',
                                '--set', 'a; b', '--pop', 'c; d',
                                'file1.json', 'file2.json']):
            actual_args = jsonfmt.parse_cmdline_args().parse_args()
            self.assertEqual(actual_args, expected_args)

    ############################################################################
    #                                 main test                                #
    ############################################################################

    @patch.multiple(sys, argv=['jf', '-i', 't', '-p', 'actions[*].name',
                               JSON_FILE, YAML_FILE])
    @patch.multiple(sys, stdout=StdOut())
    def test_main_with_file(self):
        json_output = color('[\n\t"eating",\n\t"sporting",\n\t"sleeping"\n]', 'json')
        yaml_output = color('- eating\n- sporting\n- sleeping', 'yaml')
        jsonfmt.main()
        output = sys.stdout.read()
        self.assertIn(json_output, output)
        self.assertIn(yaml_output, output)

    def test_main_with_stdin(self):
        with patch.multiple(sys, argv=['jf', '-f', 'yaml'],
                            stdin=StdIn('["a", "b"]'), stdout=StdOut()):
            expected_output = color('- a\n- b', 'yaml')
            jsonfmt.main()
            self.assertEqual(sys.stdout.read(), expected_output)

    @patch.multiple(sys, stderr=StdErr())
    def test_main_invalid_input(self):
        # test not exist file and wrong format
        with patch.multiple(sys, argv=['jf', 'not_exist_file.json', __file__]):
            jsonfmt.main()
            errmsg = sys.stderr.read()
            self.assertIn("No such file or directory: 'not_exist_file.json'", errmsg)
            self.assertIn('no supported format found', errmsg)

        with patch.multiple(sys, argv=['jf']), \
                patch('sys.stdin.read', side_effect=KeyboardInterrupt), \
                self.assertRaises(SystemExit):
            jsonfmt.main()
        self.assertIn('user canceled', sys.stderr.read())

    @patch.multiple(sys, stderr=StdErr())
    def test_main_querying(self):
        # test empty jmespath
        with patch('sys.argv', ['jf', JSON_FILE, '-p', '$.-[=]']), \
                self.assertRaises(SystemExit):
            jsonfmt.main()
        self.assertIn('invalid querypath expression', sys.stderr.read())

        # test empty jmespath
        with patch('sys.argv', ['jf', JSON_FILE, '-l', 'jsonpath', '-p', ' ']), \
                self.assertRaises(SystemExit):
            jsonfmt.main()
        self.assertIn('invalid querypath expression', sys.stderr.read())

    @patch('sys.stdout', StdOut())
    def test_main_convert(self):
        # test json to toml
        with patch.multiple(sys, argv=['jf', '-f', 'toml', JSON_FILE]):
            jsonfmt.main()
            self.assertEqual(sys.stdout.read(), color(TOML_TEXT, 'toml'))

        # test toml to xml
        with patch.multiple(sys, argv=['jf', '-f', 'xml', TOML_FILE]):
            jsonfmt.main()
            self.assertEqual(sys.stdout.read(), color(XML_TEXT, 'xml'))

        # test xml to yaml
        with patch.multiple(sys, argv=['jf', '-f', 'yaml', XML_FILE]):
            jsonfmt.main()
            self.assertEqual(sys.stdout.read(), color(YAML_TEXT, 'yaml'))

        # test yaml to json
        with patch.multiple(sys, argv=['jf', '-c', '-f', 'json', YAML_FILE]):
            jsonfmt.main()
            self.assertEqual(sys.stdout.read(), color(JSON_TEXT, 'json'))

    @patch.multiple(sys, argv=['jf', '-oc'])
    @patch.multiple(sys,
                    stdin=StdIn('{"a": "asfd", "b": [1, 2, 3]}'),
                    stdout=StdOut(tty=False))
    def test_main_overview(self):
        jsonfmt.main()
        self.assertEqual(sys.stdout.read().strip(), '{"a":"...","b":[]}')

    @patch('sys.argv', ['jf', '-Ocf', 'json', TOML_FILE])
    def test_main_overwrite_to_original_file(self):
        try:
            jsonfmt.main()
            with open(TOML_FILE) as toml_fp:
                new_content = toml_fp.read().strip()
            self.assertEqual(new_content, JSON_TEXT.strip())
        finally:
            with open(TOML_FILE, 'w') as toml_fp:
                toml_fp.write(TOML_TEXT)

    @patch.multiple(sys, argv=['jf', '-Cc', JSON_FILE, TOML_FILE])
    def test_main_copy_to_clipboard(self):
        if jsonfmt.is_clipboard_available():
            pyperclip.copy('')
            jsonfmt.main()
            copied_text = pyperclip.paste().strip()
            self.assertEqual(copied_text, JSON_TEXT.strip() + '\n\n\n' + TOML_TEXT.strip())

    @patch.multiple(jsonfmt, is_clipboard_available=lambda: False)
    @patch.multiple(sys, stderr=StdErr())
    @patch.multiple(sys, argv=['jf', JSON_FILE, '-cC'])
    def test_main_clipboard_unavailable(self):
        errmsg = '\033[1;91mjsonfmt:\033[0m \033[0;91mclipboard unavailable\033[0m\n'
        with self.assertRaises(SystemExit):
            jsonfmt.main()
        self.assertEqual(sys.stderr.read(), errmsg)

    @patch.multiple(sys,
                    argv=['jf',
                          '--set', 'age=32; box=[1,2,3]',
                          '--pop', 'money; actions.1'])
    @patch.multiple(sys, stdin=StdIn(JSON_TEXT), stdout=StdOut(tty=False))
    def test_main_modify_and_pop(self):
        try:
            jsonfmt.main()
            py_obj = json.loads(sys.stdout.read())
            self.assertEqual(py_obj['age'], 32)
            self.assertEqual(py_obj['box'], [1, 2, 3])
            self.assertNotIn('money', py_obj)
            self.assertEqual(len(py_obj['actions']), 2)
        finally:
            with open(JSON_FILE, 'w') as fp:
                fp.write(JSON_TEXT)

    @patch.multiple(sys, stdout=StdOut(), stderr=StdErr())
    def test_main_diff_mode(self):
        # right way
        with patch.multiple(sys, argv=['jf', '-D', 'diff', JSON_FILE, XML_FILE]), \
                self.assertNotRaises(SystemExit):
            jsonfmt.main()

        # wrong args
        with patch.multiple(sys, argv=['jf', '-D', 'diff', XML_FILE]), \
                self.assertRaises(SystemExit):
            jsonfmt.main()
        self.assertIn('less than two files', sys.stderr.read())

        with patch.multiple(sys, argv=['jf', '-D', 'nothing', XML_FILE, TOML_FILE]), \
                self.assertRaises(SystemExit):
            jsonfmt.main()
        self.assertIn("No such file or directory: 'nothing'", sys.stderr.read())


if __name__ == "__main__":
    unittest.main()
