import json
import os
import sys
import tempfile
import unittest
from argparse import Namespace
from copy import deepcopy
from functools import partial
from io import StringIO
from unittest.mock import patch

import pyperclip
from jmespath import compile as jcompile
from jsonpath_ng import parse as jparse
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, TOMLLexer, YamlLexer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from jsonfmt import jsonfmt

JSON_FILE = f'{BASE_DIR}/test/example.json'
with open(JSON_FILE) as json_fp:
    JSON_TEXT = json_fp.read()

TOML_FILE = f'{BASE_DIR}/test/example.toml'
with open(TOML_FILE) as toml_fp:
    TOML_TEXT = toml_fp.read()

YAML_FILE = f'{BASE_DIR}/test/example.yaml'
with open(YAML_FILE) as yaml_fp:
    YAML_TEXT = yaml_fp.read()


def color(text, fmt):
    fn = {
        'json': partial(highlight,
                        lexer=JsonLexer(),
                        formatter=TerminalFormatter()),
        'toml': partial(highlight,
                        lexer=TOMLLexer(),
                        formatter=TerminalFormatter()),
        'yaml': partial(highlight,
                        lexer=YamlLexer(),
                        formatter=TerminalFormatter()),
    }[fmt]
    return fn(text)


class FakeStdStream(StringIO):

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


class FakeStdIn(FakeStdStream):
    name = '<stdin>'

    def fileno(self) -> int:
        return 0


class FakeStdOut(FakeStdStream):
    name = '<stdout>'

    def fileno(self) -> int:
        return 1


class FakeStdErr(FakeStdStream):
    name = '<stderr>'

    def fileno(self) -> int:
        return 2


class JSONFormatToolTestCase(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.py_obj = json.loads(JSON_TEXT)

    def test_is_clipboard_available(self):
        available = jsonfmt.is_clipboard_available()
        self.assertIsInstance(available, bool)

    def test_parse_to_pyobj_with_jmespath(self):
        # normal parameters test
        matched_obj = jsonfmt.parse_to_pyobj(JSON_TEXT, jcompile("actions[:].calorie"))
        self.assertEqual(matched_obj, ([294.9, -375], 'json'))
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, jcompile("actions[*].name"))
        self.assertEqual(matched_obj, (['eat', 'sport'], 'toml'))
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jcompile("actions[*].date"))
        self.assertEqual(matched_obj, (['2021-03-02', '2023-04-27'], 'yaml'))
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
        self.assertEqual(matched_obj, (['Bob', 'eat', 'sport'], 'toml'))
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, jparse("actions[*].date"))
        self.assertEqual(matched_obj, (['2021-03-02', '2023-04-27'], 'yaml'))
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
        jsonfmt.modify_pyobj(obj, ['actions[20]={"K":"V"}'], [])
        self.assertEqual(obj['actions'][2], {"K": "V"})
        # add multiple values at once
        jsonfmt.modify_pyobj(obj, ['new=[1,2,3]', 'actions[50]={"K":"V"}'], [])
        self.assertEqual(obj['new'], [1, 2, 3])
        self.assertEqual(obj['actions'][2], {"K": "V"})

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
        # pop single value
        jsonfmt.modify_pyobj(obj, [], ['age'])
        self.assertNotIn('age', obj)
        # pop multiple values at once
        jsonfmt.modify_pyobj(obj, [], ['money', 'actions[1]', 'actions.0.date'])
        self.assertNotIn('money', obj)
        self.assertNotIn('date', obj['actions'][0])
        self.assertEqual(1, len(obj['actions']))

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
        with patch('jsonfmt.stderr', FakeStdErr()):
            # modifying
            jsonfmt.modify_pyobj(obj, ['aa.bb=empty'], [])
            self.assertIn('invalid key path', jsonfmt.stderr.read())
            # popping
            jsonfmt.modify_pyobj(obj, [], ['actions[3]'])
            self.assertIn('invalid key path', jsonfmt.stderr.read())

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
                "calorie": 294.9,
                "date": "...",
                "name": "..."
            }
        ]
        overview = jsonfmt.get_overview(obj)
        self.assertEqual(overview, expected_2)

    def test_format_to_text(self):
        py_obj = {"name": "约翰", "age": 30}
        # format to json (compacted)
        j_compacted = jsonfmt.format_to_text(py_obj, 'json',
                                             compact=True, escape=True,
                                             indent=4, sort_keys=False)
        self.assertEqual(j_compacted.strip(), '{"name":"\\u7ea6\\u7ff0","age":30}')

        # format to json (indentation)
        j_indented = jsonfmt.format_to_text(py_obj, 'json',
                                            compact=False, escape=False,
                                            indent=4, sort_keys=True)
        self.assertEqual(j_indented.strip(), '{\n    "age": 30,\n    "name": "约翰"\n}')

        # format to toml
        toml_text = jsonfmt.format_to_text(self.py_obj, 'toml',
                                           compact=False, escape=False,
                                           indent=4, sort_keys=False)
        self.assertEqual(toml_text.strip(), TOML_TEXT.strip())

        # format to yaml
        yaml_text = jsonfmt.format_to_text(self.py_obj, 'yaml',
                                           compact=False, escape=False,
                                           indent=2, sort_keys=True)
        self.assertEqual(yaml_text.strip(), YAML_TEXT.strip())

        # test exceptions
        with self.assertRaises(jsonfmt.FormatError):
            jsonfmt.format_to_text([1, 2, 3], 'toml',
                                   compact=False, escape=False,
                                   indent=4, sort_keys=False)

        with self.assertRaises(jsonfmt.FormatError):
            jsonfmt.format_to_text(py_obj, 'xml',
                                   compact=False, escape=False,
                                   indent=4, sort_keys=False)

    def test_output(self):
        # output JSON to clipboard
        if jsonfmt.is_clipboard_available():
            with patch('jsonfmt.stdout', FakeStdOut()):
                jsonfmt.output(jsonfmt.stdout, JSON_TEXT, 'json', True)
                self.assertEqual(pyperclip.paste(), JSON_TEXT)

        # output TOML to file (temp file)
        with tempfile.NamedTemporaryFile(mode='r+') as tmpfile:
            jsonfmt.output(tmpfile, TOML_TEXT, 'toml', False)
            tmpfile.seek(0)
            self.assertEqual(tmpfile.read(), TOML_TEXT)

        # output YAML to stdout (mock)
        with patch('jsonfmt.stdout', FakeStdOut()):
            jsonfmt.output(jsonfmt.stdout, YAML_TEXT, 'yaml', False)
            self.assertEqual(jsonfmt.stdout.read(), color(YAML_TEXT, 'yaml'))

        # output unknow format
        with self.assertRaises(KeyError), patch('jsonfmt.stdout', FakeStdOut()):
            jsonfmt.output(jsonfmt.stdout, YAML_TEXT, 'xml', False)

    def test_parse_cmdline_args(self):
        # test default parameters
        default_args = Namespace(
            compact=False,
            cp2clip=False,
            escape=False,
            format=None,
            indent='2',
            overview=False,
            overwrite=False,
            querylang='jmespath',
            querypath=None,
            sort_keys=False,
            set=None,
            pop=None,
            files=[]
        )
        actual_args = jsonfmt.parse_cmdline_args(args=[])
        self.assertEqual(actual_args, default_args)

        # test specified parameters
        args = [
            '-c',
            '-C',
            '-e',
            '-f', 'toml',
            '-i', '4',
            '-o',
            '-O',
            '-l', 'jsonpath',
            '-p', 'path.to.json',
            '--set', 'a; b',
            '--pop', 'c; d',
            '-s',
            'file1.json',
            'file2.json'
        ]
        expected_args = Namespace(
            compact=True,
            cp2clip=True,
            escape=True,
            format='toml',
            indent='4',
            overview=True,
            overwrite=True,
            querylang='jsonpath',
            querypath='path.to.json',
            sort_keys=True,
            set='a; b',
            pop='c; d',
            files=['file1.json', 'file2.json']
        )

        actual_args = jsonfmt.parse_cmdline_args(args=args)
        self.assertEqual(actual_args, expected_args)

    ############################################################################
    #                                 main test                                #
    ############################################################################

    @patch.multiple(sys, argv=['jsonfmt', '-i', 't', '-p', 'actions[*].name',
                               JSON_FILE, YAML_FILE])
    @patch.multiple(jsonfmt, stdout=FakeStdOut())
    def test_main_with_file(self):
        expected_output = color('[\n\t"eat",\n\t"sport"\n]', 'json')
        expected_output += '----------------\n'
        expected_output += color('- eat\n- sport', 'yaml')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), expected_output)

    @patch.multiple(sys, argv=['jsonfmt', '-f', 'yaml'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn('["a", "b"]'), stdout=FakeStdOut())
    def test_main_with_stdin(self):
        expected_output = color('- a\n- b', 'yaml')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), expected_output)

    @patch.multiple(jsonfmt, stderr=FakeStdErr())
    def test_main_invalid_input(self):
        # test not exist file and wrong format
        with patch.multiple(sys, argv=['jsonfmt', 'not_exist_file.json', __file__]):
            jsonfmt.main()
            errmsg = jsonfmt.stderr.read()
            self.assertIn('no such file: not_exist_file.json', errmsg)
            self.assertIn('no json, toml or yaml found', errmsg)

    @patch.multiple(jsonfmt, stderr=FakeStdErr())
    def test_main_querying(self):
        # test empty jmespath
        with patch('sys.argv', ['jsonfmt', JSON_FILE, '-p', '$.-[=]']),\
                self.assertRaises(SystemExit):
            jsonfmt.main()
        self.assertIn('invalid querypath expression', jsonfmt.stderr.read())

        # test empty jmespath
        with patch('sys.argv', ['jsonfmt', JSON_FILE, '-l', 'jsonpath', '-p', ' ']),\
                self.assertRaises(SystemExit):
            jsonfmt.main()
        self.assertIn('invalid querypath expression', jsonfmt.stderr.read())

    @patch('jsonfmt.stdout', FakeStdOut())
    def test_main_convert(self):
        # test json to toml
        with patch.multiple(sys, argv=['jsonfmt', '-f', 'toml', JSON_FILE]):
            colored_output = color(TOML_TEXT, 'toml')
            jsonfmt.main()
            self.assertEqual(jsonfmt.stdout.read(), colored_output)

        # test toml to yaml
        with patch.multiple(sys, argv=['jsonfmt', '-s', '-f', 'yaml', TOML_FILE]):
            colored_output = color(YAML_TEXT, 'yaml')
            jsonfmt.main()
            self.assertEqual(jsonfmt.stdout.read(), colored_output)

        # test yaml to json
        with patch.multiple(sys, argv=['jsonfmt', '-c', '-f', 'json', YAML_FILE]):
            colored_output = color(JSON_TEXT, 'json')
            jsonfmt.main()
            self.assertEqual(jsonfmt.stdout.read(), colored_output)

    @patch.multiple(sys, argv=['jsonfmt', '-oc'])
    @patch.multiple(jsonfmt,
                    stdin=FakeStdIn('{"a": "asfd", "b": [1, 2, 3]}'),
                    stdout=FakeStdOut(tty=False))
    def test_main_overview(self):
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read().strip(), '{"a":"...","b":[]}')

    @patch('sys.argv', ['jsonfmt', '-Ocsf', 'json', TOML_FILE])
    def test_main_overwrite_to_original_file(self):
        try:
            jsonfmt.main()
            with open(TOML_FILE) as toml_fp:
                new_content = toml_fp.read().strip()
            self.assertEqual(new_content, JSON_TEXT.strip())
        finally:
            with open(TOML_FILE, 'w') as toml_fp:
                toml_fp.write(TOML_TEXT)

    @patch.multiple(jsonfmt, stdout=FakeStdOut(), stderr=FakeStdErr())
    def test_main_copy_to_clipboard(self):
        if jsonfmt.is_clipboard_available():
            with patch("sys.argv", ['jsonfmt', '-Ccs', JSON_FILE]):
                jsonfmt.main()
                copied_text = pyperclip.paste().strip()
                self.assertEqual(copied_text, JSON_TEXT.strip())

            with patch("sys.argv", ['jsonfmt', '-Cs', TOML_FILE]):
                jsonfmt.main()
                copied_text = pyperclip.paste().strip()
                self.assertEqual(copied_text, TOML_TEXT.strip())

            with patch("sys.argv", ['jsonfmt', '-Cs', YAML_FILE]):
                jsonfmt.main()
                copied_text = pyperclip.paste().strip()
                self.assertEqual(copied_text, YAML_TEXT.strip())

    @patch.multiple(jsonfmt, is_clipboard_available=lambda: False)
    @patch.multiple(jsonfmt, stdout=FakeStdOut(), stderr=FakeStdErr())
    @patch.multiple(sys, argv=['jsonfmt', JSON_FILE, '-cC'])
    def test_main_clipboard_unavailable(self):
        errmsg = '\033[1;91mjsonfmt:\033[0m \033[0;91mclipboard unavailable\033[0m\n'
        jsonfmt.main()
        self.assertEqual(jsonfmt.stderr.read(), errmsg)
        self.assertEqual(jsonfmt.stdout.read(), color(JSON_TEXT, 'json'))

    @patch.multiple(sys,
                    argv=['jsonfmt',
                          '--set', 'age=32; box=[1,2,3]',
                          '--pop', 'money; actions.1'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn(JSON_TEXT), stdout=FakeStdOut(tty=False))
    def test_main_modify_and_pop(self):
        try:
            jsonfmt.main()
            py_obj = json.loads(jsonfmt.stdout.read())
            self.assertEqual(py_obj['age'], 32)
            self.assertEqual(py_obj['box'], [1, 2, 3])
            self.assertNotIn('money', py_obj)
            self.assertEqual(len(py_obj['actions']), 1)
        finally:
            with open(JSON_FILE, 'w') as fp:
                fp.write(JSON_TEXT)


if __name__ == "__main__":
    unittest.main()
