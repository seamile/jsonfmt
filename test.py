import json
import tempfile
import unittest
from jsonfmt import (JSONPathError, parse_jsonpath,
                     match_element, read_json_to_py, output)


class JSONFormatToolTestCase(unittest.TestCase):
    def setUp(self):
        with open('example.json') as json_fp:
            self.example_obj = json.load(json_fp)

    def test_parse_jsonpath(self):
        empty_path = ""
        expected_components = []
        components = parse_jsonpath(empty_path)
        self.assertEqual(components, expected_components)

        jsonpath = "history/0/items/*/name"
        expected_components = ["history", 0, "items", "*", "name"]
        components = parse_jsonpath(jsonpath)
        self.assertEqual(components, expected_components)

    def test_match_element(self):
        components = ["history", 0, "items", 1, "calorie"]
        expected_element = 266
        element = match_element(self.example_obj, components)
        self.assertEqual(element, expected_element)

        with self.assertRaises(JSONPathError):
            match_element(self.example_obj, ['unexist_key'])

    def test_read_json_to_py(self):
        jsonpath = "history/*/items/1/calorie"
        expected_matched_obj = [266, 54.5, -350]
        with open('example.json') as json_fp:
            matched_obj = read_json_to_py(json_fp, jsonpath)
            self.assertEqual(matched_obj, expected_matched_obj)

        with open('example.json') as json_fp:
            matched_obj = read_json_to_py(json_fp, "/")
            self.assertEqual(matched_obj, self.example_obj)

        with open('example.json') as json_fp:
            matched_obj = read_json_to_py(json_fp, "unexist_key")
            self.assertEqual(matched_obj, None)

        with open(__file__) as json_fp:
            matched_obj = read_json_to_py(json_fp, jsonpath)
            self.assertEqual(matched_obj, None)

    def test_output(self):
        json_obj = {"name": "John", "age": 30}
        expected_output = '{"age":30,"name":"John"}\n'

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='r+') as temp_file:
            # Call the output function with the temporary file
            output(json_obj, True, False, 4, temp_file)

            # Read the content of the temporary file
            temp_file.seek(0)
            output_str = temp_file.read()

            # Check the output content
            self.assertEqual(output_str, expected_output)


if __name__ == '__main__':
    unittest.main()
