import json
import os
import sys
import tempfile
import unittest
import pyperclip
from argparse import Namespace
from copy import deepcopy
from functools import partial
from io import StringIO
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, YamlLexer, TOMLLexer
from unittest.mock import patch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
import jsonfmt


with open(f'{BASE_DIR}/test/example.json') as json_fp:
    JSON_TEXT = json_fp.read()

with open(f'{BASE_DIR}/test/example.toml') as toml_fp:
    TOML_TEXT = toml_fp.read()

with open(f'{BASE_DIR}/test/example.yaml') as yaml_fp:
    YAML_TEXT = yaml_fp.read()


def color(text, format):
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
    }[format]
    return fn(text)


class FakeStdStream(StringIO):
    def isatty(self):
        return True

    def read(self):
        self.seek(0)
        return super().read()


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

    def test_parse_to_pyobj(self):
        # normal parameters test
        matched_obj = jsonfmt.parse_to_pyobj(JSON_TEXT, "$.actions[:].calorie")
        self.assertEqual(matched_obj, ([294.9, -375], 'json'))
        matched_obj = jsonfmt.parse_to_pyobj(TOML_TEXT, "$.actions.*.name")
        self.assertEqual(matched_obj, (['eat', 'sport'], 'toml'))
        matched_obj = jsonfmt.parse_to_pyobj(YAML_TEXT, "$.actions.*.date")
        self.assertEqual(matched_obj, (['2021-03-02', '2023-04-27'], 'yaml'))

        # exception test
        with patch('jsonfmt.stderr', FakeStdErr()):
            # test empty jsonpath
            with self.assertRaises(jsonfmt.JsonPathError):
                matched_obj = jsonfmt.parse_to_pyobj(JSON_TEXT, "")

            # test not exists key
            with self.assertRaises(jsonfmt.JsonPathError):
                jsonfmt.parse_to_pyobj(TOML_TEXT, "$.not_exist_key")

            # test index out of range
            with self.assertRaises(jsonfmt.JsonPathError):
                jsonfmt.parse_to_pyobj(YAML_TEXT, '$.actions[7]')

        # test non-json file
        with self.assertRaises(jsonfmt.ParseError), open(__file__) as fp:
            text = fp.read()
            matched_obj = jsonfmt.parse_to_pyobj(text, "$.actions[0].calorie")

    def test_modify_pyobj_for_adding(self):
        # test empty sets and pops
        obj = deepcopy(self.py_obj)
        jsonfmt.modify_pyobj(obj, [], [])
        self.assertEqual(obj, self.py_obj)

        # test add new value
        obj = deepcopy(self.py_obj)
        # add single value
        jsonfmt.modify_pyobj(obj, ['new1=value1'], [])
        self.assertEqual(obj['new1'], 'value1')
        # add multiple values at once
        jsonfmt.modify_pyobj(obj, ['new2={}', 'new3=[1,2,3]'], [])
        self.assertEqual(obj['new2'], {})
        self.assertEqual(obj['new3'], [1, 2, 3])

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
        obj = deepcopy(self.py_obj)
        obj['dict'] = {"a": 7758, "b": [1, 2, 3]}
        expected = {
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
        self.assertEqual(overview, expected)

    def test_format_to_text(self):
        py_obj = {"name": "约翰", "age": 30}
        # format to json (compacted)
        j_compacted = jsonfmt.format_to_text(py_obj, 'json',
                                             compact=True, escape=True,
                                             indent=4, sort_keys=False)
        self.assertEqual(j_compacted, '{"name":"\\u7ea6\\u7ff0","age":30}')

        # format to json (indentation)
        j_indented = jsonfmt.format_to_text(py_obj, 'json',
                                            compact=False, escape=False,
                                            indent=4, sort_keys=True)
        self.assertEqual(j_indented, '{\n    "age": 30,\n    "name": "约翰"\n}')

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
        with self.assertRaises(jsonfmt.ParseError):
            jsonfmt.format_to_text([1, 2, 3], 'toml',
                                   compact=False, escape=False,
                                   indent=4, sort_keys=False)

        with self.assertRaises(jsonfmt.ParseError):
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
            jsonpath=None,
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
            '-p', 'path/to/json',
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
            jsonpath='path/to/json',
            sort_keys=True,
            set='a; b',
            pop='c; d',
            files=['file1.json', 'file2.json']
        )

        actual_args = jsonfmt.parse_cmdline_args(args=args)
        self.assertEqual(actual_args, expected_args)

    @patch.multiple(sys, argv=['jsonfmt', '-i', 't', '-p', '$.name',
                               f'{BASE_DIR}/test/example.json'])
    @patch.multiple(jsonfmt, stdout=FakeStdOut())
    def test_main_with_file(self):
        expected_output = color('[\n\t"Bob"\n]', 'json')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), expected_output)

    @patch.multiple(sys, argv=['jsonfmt', '-f', 'yaml'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn('["a", "b"]'), stdout=FakeStdOut())
    def test_main_with_stdin(self):
        expected_output = color('- a\n- b', 'yaml')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), expected_output)

    @patch.multiple(sys, argv=['jsonfmt', 'not_exist_file.json', __file__])
    @patch.multiple(jsonfmt, stderr=FakeStdErr())
    def test_main_invalid_file(self):
        jsonfmt.main()
        errmsg = jsonfmt.stderr.read()
        self.assertIn('no such file `not_exist_file.json`', errmsg)
        self.assertIn('no json, toml or yaml found', errmsg)

    @patch.multiple(sys, argv=['jsonfmt', '-f', 'json'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn(']a, b, c]'), stderr=FakeStdErr())
    def test_main_invalid_input(self):
        jsonfmt.main()
        self.assertIn('no json, toml or yaml found', jsonfmt.stderr.read())

    @patch.multiple(sys, argv=['jsonfmt', '-f', 'toml'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn(JSON_TEXT), stdout=FakeStdOut())
    def test_json_to_toml(self):
        colored_output = color(TOML_TEXT, 'toml')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), colored_output)

    @patch.multiple(sys, argv=['jsonfmt', '-s', '-f', 'yaml'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn(TOML_TEXT), stdout=FakeStdOut())
    def test_toml_to_yaml(self):
        colored_output = color(YAML_TEXT, 'yaml')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), colored_output)

    @patch.multiple(sys, argv=['jsonfmt', '-c', '-f', 'json'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn(YAML_TEXT), stdout=FakeStdOut())
    def test_yaml_to_json(self):
        colored_output = color(JSON_TEXT, 'json')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), colored_output)

    @patch.multiple(sys, argv=['jsonfmt', '-Ocsf', 'json',
                               f'{BASE_DIR}/test/example.toml'])
    def test_overwrite_to_original_file(self):
        try:
            jsonfmt.main()
            with open(f'{BASE_DIR}/test/example.toml') as toml_fp:
                new_content = toml_fp.read().strip()
            self.assertEqual(new_content, JSON_TEXT.strip())
        finally:
            with open(f'{BASE_DIR}/test/example.toml', 'w') as toml_fp:
                toml_fp.write(TOML_TEXT)

    @patch.multiple(jsonfmt, stdout=FakeStdOut(), stderr=FakeStdErr())
    def test_copy_to_clipboard(self):
        if jsonfmt.is_clipboard_available():
            with patch("sys.argv",
                       ['jsonfmt', '-Ccs', f'{BASE_DIR}/test/example.json']):
                jsonfmt.main()
                copied_text = pyperclip.paste().strip()
                self.assertEqual(copied_text, JSON_TEXT.strip())

            with patch("sys.argv",
                       ['jsonfmt', '-Cs', f'{BASE_DIR}/test/example.toml']):
                jsonfmt.main()
                copied_text = pyperclip.paste().strip()
                self.assertEqual(copied_text, TOML_TEXT.strip())

            with patch("sys.argv",
                       ['jsonfmt', '-Cs', f'{BASE_DIR}/test/example.yaml']):
                jsonfmt.main()
                copied_text = pyperclip.paste().strip()
                self.assertEqual(copied_text, YAML_TEXT.strip())

    @patch.multiple(jsonfmt, is_clipboard_available=lambda: False)
    @patch.multiple(jsonfmt, stdout=FakeStdOut(), stderr=FakeStdErr())
    @patch.multiple(sys, argv=['jsonfmt', f'{BASE_DIR}/test/example.json', '-cC'])
    def test_clipboard_unavailable(self):
        errmsg = '\033[1;91mjsonfmt:\033[0m \033[0;91mclipboard unavailable\033[0m\n'
        jsonfmt.main()
        self.assertEqual(jsonfmt.stderr.read(), errmsg)
        self.assertEqual(jsonfmt.stdout.read(), color(JSON_TEXT, 'json'))

    @patch.multiple(sys, argv=['jsonfmt', '-O', f'{BASE_DIR}/test/example.json',
                               '--set', 'age=32; box=[1,2,3]',
                               '--pop', 'money; actions.1'])
    def test_modify_and_pop(self):
        try:
            jsonfmt.main()
            with open(f'{BASE_DIR}/test/example.json') as fp:
                py_obj = json.load(fp)
            self.assertEqual(py_obj['age'], 32)
            self.assertEqual(py_obj['box'], [1, 2, 3])
            self.assertNotIn('money', py_obj)
            self.assertEqual(len(py_obj['actions']), 1)
        finally:
            with open(f'{BASE_DIR}/test/example.json', 'w') as fp:
                fp.write(JSON_TEXT)


if __name__ == "__main__":
    unittest.main()
