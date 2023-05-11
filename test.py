import json
import tempfile
import unittest
from jsonfmt import (parse_jsonpath, get_element_by_components,
                     jsonpath_match, output)


class JSONFormatToolTestCase(unittest.TestCase):
    def setUp(self):
        with open('example.json') as json_fp:
            self.example_json = json.load(json_fp)

    def test_parse_jsonpath(self):
        jsonpath = "history/0/items/2/name"
        expected_components = ["history", 0, "items", 2, "name"]
        components = parse_jsonpath(jsonpath)
        self.assertEqual(components, expected_components)

    def test_get_element_by_components(self):
        components = ["history", 0, "items", 1, "calorie"]
        expected_element = 266
        element = get_element_by_components(self.example_json, components)
        self.assertEqual(element, expected_element)

    def test_jsonpath_match(self):
        jsonpath = "history/*/items/1/calorie"
        expected_matched_obj = [266, 54.5, -350]
        matched_obj = jsonpath_match(self.example_json, jsonpath)
        self.assertEqual(matched_obj, expected_matched_obj)

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
