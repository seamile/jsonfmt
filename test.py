import json
import sys
import tempfile
import unittest
from argparse import Namespace
from io import StringIO
from unittest.mock import patch

import jsonfmt


class FakeStdIn(StringIO):
    def isatty(self):
        return True

    def fileno(self):
        return 0


class FakeStdout(StringIO):
    def isatty(self):
        return True

    def fileno(self):
        return 1

    def read(self):
        self.seek(0)
        return super().read()


class JSONFormatToolTestCase(unittest.TestCase):
    def setUp(self):
        with open('example.json') as json_fp:
            self.example_obj = json.load(json_fp)

    def test_parse_jsonpath(self):
        # empty path
        empty_path = ""
        expected_components = []
        components = jsonfmt.parse_jsonpath(empty_path)
        self.assertEqual(components, expected_components)
        # the jsonpath contains key, index and '*'
        jsonpath = "history/0/items/*/name"
        expected_components = ["history", 0, "items", "*", "name"]
        components = jsonfmt.parse_jsonpath(jsonpath)
        self.assertEqual(components, expected_components)

    def test_match_element(self):
        components = ["history", 0, "items", 1, "calorie"]
        expected_element = 266
        element = jsonfmt.match_element(self.example_obj, components)
        self.assertEqual(element, expected_element)

        with self.assertRaises(jsonfmt.JSONPathError):
            jsonfmt.match_element(self.example_obj, ['not_exist_key'])

    def test_read_json_to_py(self):
        jsonpath = "history/*/items/1/calorie"
        expected_matched_obj = [266, 54.5, -350]

        # normal parameters
        with open('example.json') as json_fp:
            matched_obj = jsonfmt.read_json_to_py(json_fp, jsonpath)
            self.assertEqual(matched_obj, expected_matched_obj)

        # test empty jsonpath
        with open('example.json') as json_fp:
            matched_obj = jsonfmt.read_json_to_py(json_fp, "/")
            self.assertEqual(matched_obj, self.example_obj)

        # test not exists key
        with (open('example.json') as json_fp,
              self.assertRaises(jsonfmt.JSONParseError)):
            jsonfmt.read_json_to_py(json_fp, "not_exist_key")

        # test non-json file
        with open(__file__) as json_fp, self.assertRaises(jsonfmt.JSONParseError):
            matched_obj = jsonfmt.read_json_to_py(json_fp, jsonpath)

    @patch('jsonfmt.stdout', FakeStdout())
    def test_output(self):
        json_obj = {"name": "John", "age": 30}

        # jsonfmt.output to stdout (mock)
        compact_and_colored = '{\x1b[94m"age"\x1b[39;49;00m:\x1b[34m30\x1b[39;49;00m,\x1b[94m"name"\x1b[39;49;00m:\x1b[33m"John"\x1b[39;49;00m}\x1b[37m\x1b[39;49;00m\n'
        jsonfmt.output(json_obj, True, False, 4, jsonfmt.stdout)
        self.assertEqual(jsonfmt.stdout.read(), compact_and_colored)

        # Create a temporary file
        with_indent_output = '{\n "age": 30,\n "name": "John"\n}\n'
        with tempfile.NamedTemporaryFile(mode='r+') as tmpfile:
            jsonfmt.output(json_obj, False, False, 1, tmpfile)
            tmpfile.seek(0)
            output_str = tmpfile.read()
            self.assertEqual(output_str, with_indent_output)

    def test_parse_cmdline_args(self):
        # test default parameters
        default_args = Namespace(compression=False, escape=False, indent=4,
                                 overwrite=False, jsonpath='', json_files=[])
        actual_args = jsonfmt.parse_cmdline_args([])
        self.assertEqual(actual_args, default_args)

        # test specified parameters
        args = [
            '-c',
            '-e',
            '-i', '2',
            '-O',
            '-p', 'path/to/json',
            'file1.json',
            'file2.json'
        ]
        expected_args = Namespace(
            compression=True,
            escape=True,
            indent=2,
            overwrite=True,
            jsonpath='path/to/json',
            json_files=['file1.json', 'file2.json']
        )

        actual_args = jsonfmt.parse_cmdline_args(args)
        self.assertEqual(actual_args, expected_args)

    @patch.multiple(sys, argv=['jsonfmt', '-p', 'name', 'example.json'])
    @patch.multiple(jsonfmt, stdout=FakeStdout())
    def test_main_with_file(self):
        expected_output = '\x1b[33m"Bob"\x1b[39;49;00m\x1b[37m\x1b[39;49;00m\n'
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), expected_output)

    @patch.multiple(sys, argv=['jsonfmt', '-p', '1'])
    @patch.multiple(jsonfmt, stdin=FakeStdIn('["a", "b"]'), stdout=FakeStdout())
    def test_main_with_stdin(self):
        expected_output = '\x1b[33m"b"\x1b[39;49;00m\x1b[37m\x1b[39;49;00m\n'
        jsonfmt.main()
        self.assertEqual(jsonfmt.stdout.read(), expected_output)


if __name__ == '__main__':
    unittest.main()
