import json
import os
import sys
import tempfile
import unittest
import pyperclip
from argparse import Namespace
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


class FakeStdOut(FakeStdStream):
    name = '<stdout>'


class FakeStdErr(FakeStdStream):
    name = '<stderr>'


class JSONFormatToolTestCase(unittest.TestCase):
    def setUp(self):
        self.py_obj = json.loads(JSON_TEXT)

    def test_is_clipboard_available(self):
        available = jsonfmt.is_clipboard_available()
        self.assertIsInstance(available, bool)

    def test_parse_to_pyobj(self):
        with open(f'{BASE_DIR}/test/example.json') as json_fp:
            # normal parameters
            matched_obj = jsonfmt.parse_to_pyobj(json_fp, "$.actions[:].calorie")
            self.assertEqual(matched_obj, [294.9, -375])

            with patch('jsonfmt.stderr', FakeStdErr()):
                # test empty jsonpath
                with self.assertRaises(jsonfmt.ParseError):
                    json_fp.seek(0)
                    matched_obj = jsonfmt.parse_to_pyobj(json_fp, "")

                # test not exists key
                with self.assertRaises(jsonfmt.ParseError):
                    json_fp.seek(0)
                    jsonfmt.parse_to_pyobj(json_fp, "$.not_exist_key")

                # test index out of range
                with self.assertRaises(jsonfmt.ParseError):
                    json_fp.seek(0)
                    jsonfmt.parse_to_pyobj(json_fp, '$.actions[7]')

        # test non-json file
        with open(__file__) as json_fp,\
                self.assertRaises(jsonfmt.ParseError):
            matched_obj = jsonfmt.parse_to_pyobj(json_fp, "$.actions[0].calorie")

    @patch('jsonfmt.stdout', FakeStdOut())
    def test_output_json(self):
        py_obj = {"name": "约翰", "age": 30}

        # test output json to file (temp file)
        with_indent_output = '{\n "age": 30,\n "name": "\\u7ea6\\u7ff0"\n}\n'
        with tempfile.NamedTemporaryFile(mode='r+') as tmpfile:
            jsonfmt.output_json(py_obj, tmpfile, cp2clip=False,
                                compact=False, escape=True, indent=1)
            tmpfile.seek(0)
            output_str = tmpfile.read()
            self.assertEqual(output_str, with_indent_output)

        # test output json to stdout (mock)
        compact_and_colored = color('{"age":30,"name":"约翰"}', 'json')
        jsonfmt.output_json(py_obj, jsonfmt.stdout, cp2clip=False,
                            compact=True, escape=False, indent=4)
        self.assertEqual(jsonfmt.stdout.read(), compact_and_colored)

    @patch.multiple(jsonfmt, stdout=FakeStdOut(), stderr=FakeStdErr())
    def test_output_toml(self):
        py_obj = {"name": "约翰", "age": 30}
        expected_outputs = ['name = "约翰"\nage = 30\n',
                            'age = 30\nname = "约翰"\n']

        # test output toml to file (temp file)
        with tempfile.NamedTemporaryFile(mode='r+') as tmpfile:
            jsonfmt.output_toml(py_obj, tmpfile, cp2clip=False)
            tmpfile.seek(0)
            self.assertIn(tmpfile.read(), expected_outputs)

        # test output toml to stdout (mock)
        colored_outputs = [color(o, 'toml') for o in expected_outputs]
        jsonfmt.output_toml(py_obj, jsonfmt.stdout, cp2clip=False)
        self.assertIn(jsonfmt.stdout.read(), colored_outputs)

        # test SystemExit when using non-mapping
        with self.assertRaises(SystemExit) as raise_ctx:
            jsonfmt.output_toml(['foo', 'bar'], jsonfmt.stdout, cp2clip=False)
        self.assertEqual(raise_ctx.exception.code, 3)

    @patch('jsonfmt.stdout', FakeStdOut())
    def test_output_yaml(self):
        py_obj = {"name": "约翰", "age": 30}

        # test output yaml to file (temp file)
        expected_output = 'age: 30\nname: "\\u7EA6\\u7FF0"\n'
        with tempfile.NamedTemporaryFile(mode='r+') as tmpfile:
            jsonfmt.output_yaml(py_obj, tmpfile, cp2clip=False,
                                escape=True, indent=2)
            tmpfile.seek(0)
            self.assertEqual(tmpfile.read(), expected_output)

        # jsonfmt.output to stdout (mock)
        colored_output = color('age: 30\nname: 约翰\n', 'yaml')
        jsonfmt.output_yaml(py_obj, jsonfmt.stdout, cp2clip=False,
                            escape=False, indent=2)
        self.assertEqual(jsonfmt.stdout.read(), colored_output)

    def test_parse_cmdline_args(self):
        # test default parameters
        default_args = Namespace(
            compact=False,
            cp2clip=False,
            escape=False,
            format='json',
            indent=2,
            overwrite=False,
            jsonpath=None,
            files=[]
        )
        actual_args = jsonfmt.parse_cmdline_args([])
        self.assertEqual(actual_args, default_args)

        # test specified parameters
        args = [
            '-c',
            '-C',
            '-e',
            '-f', 'toml',
            '-i', '4',
            '-O',
            '-p', 'path/to/json',
            'file1.json',
            'file2.json'
        ]
        expected_args = Namespace(
            compact=True,
            cp2clip=True,
            escape=True,
            format='toml',
            indent=4,
            overwrite=True,
            jsonpath='path/to/json',
            files=['file1.json', 'file2.json']
        )

        actual_args = jsonfmt.parse_cmdline_args(args)
        self.assertEqual(actual_args, expected_args)

    @patch.multiple(sys, argv=['jsonfmt', '-i', '4', '-p', '$.name', f'{BASE_DIR}/test/example.json'])
    @patch.multiple(jsonfmt, stdout=FakeStdOut())
    def test_main_with_file(self):
        expected_output = color('[\n    "Bob"\n]', 'json')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), expected_output)

    @patch.multiple(sys, argv=['jsonfmt', '-f', 'yaml'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn('["a", "b"]'), stdout=FakeStdOut())
    def test_main_with_stdin(self):
        expected_output = color('- a\n- b', 'yaml')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), expected_output)

    @patch.multiple(sys, argv=['jsonfmt', 'foo.bar', __file__])
    @patch.multiple(jsonfmt, stderr=FakeStdErr())
    def test_main_invalid_file(self):
        with self.assertRaises(SystemExit) as raise_ctx:
            jsonfmt.main()
        self.assertEqual(raise_ctx.exception.code, 1)

    @patch.multiple(sys, argv=['jsonfmt', '-f', 'json'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn(']a, b, c]'), stderr=FakeStdErr())
    def test_main_invalid_input(self):
        with self.assertRaises(SystemExit) as raise_ctx:
            jsonfmt.main()
        self.assertEqual(raise_ctx.exception.code, 2)

    @patch.multiple(sys, argv=['jsonfmt', '-f', 'toml'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn(JSON_TEXT), stdout=FakeStdOut())
    def test_json_to_toml(self):
        colored_output = color(TOML_TEXT, 'toml')
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), colored_output)

    @patch.multiple(sys, argv=['jsonfmt', '-f', 'yaml'])
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

    @patch.multiple(sys, argv=['jsonfmt', '-cO', f'{BASE_DIR}/test/example.toml'])
    def test_overwrite_to_original_file(self):
        try:
            jsonfmt.main()
            with open(f'{BASE_DIR}/test/example.toml') as toml_fp:
                new_content = toml_fp.read()
            self.assertEqual(new_content, JSON_TEXT)
        finally:
            with open(f'{BASE_DIR}/test/example.toml', 'w') as toml_fp:
                toml_fp.write(TOML_TEXT)

    @patch.multiple(jsonfmt, stdout=FakeStdOut(), stderr=FakeStdErr())
    def test_copy_to_clipboard(self):
        if jsonfmt.is_clipboard_available():
            with patch("sys.argv", ['jsonfmt', f'{BASE_DIR}/test/example.toml', '-Cc']):
                jsonfmt.main()
                copied_text = pyperclip.paste().strip()
                self.assertEqual(copied_text, JSON_TEXT.strip())

            with patch("sys.argv", ['jsonfmt', f'{BASE_DIR}/test/example.json', '-Cf', 'toml']):
                jsonfmt.main()
                copied_text = pyperclip.paste().strip()
                self.assertEqual(copied_text, TOML_TEXT.strip())

            with patch("sys.argv", ['jsonfmt', f'{BASE_DIR}/test/example.json', '-Cf', 'yaml']):
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


if __name__ == '__main__':
    unittest.main()
