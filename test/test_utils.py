
import sys
import unittest
from unittest import mock
from collections import OrderedDict
from io import StringIO

from jsonfmt.utils import exit_with_error, print_inf, safe_eval, sort_dict


class TestFunctions(unittest.TestCase):

    def test_safe_eval(self):
        self.assertEqual(safe_eval("{'a': 1, 'b': 2}"), {'a': 1, 'b': 2})
        self.assertEqual(safe_eval("[1, 2, 3]"), [1, 2, 3])
        self.assertEqual(safe_eval("'hello'"), 'hello')
        self.assertEqual(safe_eval("invalid_syntax"), "invalid_syntax")

    def test_sort_dict(self):
        self.assertEqual(sort_dict({'c': 3, 'a': 1, 'b': 2}),
                         OrderedDict([('a', 1), ('b', 2), ('c', 3)]))
        self.assertEqual(sort_dict([{'z': 3, 'y': 2, 'x': 1}, {'w': 4}]),
                         [{'x': 1, 'y': 2, 'z': 3}, {'w': 4}])
        self.assertEqual(sort_dict(5), 5)

    @mock.patch('sys.stderr', new=StringIO())
    def test_print_inf(self):
        print_inf("This is an info message")
        self.assertEqual(sys.stderr.getvalue(),  # type: ignore
                         "\033[0;94mThis is an info message\033[0m\n")

    @mock.patch('sys.stderr', new=StringIO())
    def test_exit_with_error(self):
        with self.assertRaises(SystemExit) as cm:
            exit_with_error("An error occurred!")
        self.assertEqual(cm.exception.code, 1)
        self.assertEqual(sys.stderr.getvalue(),  # type: ignore
                         "\033[1;91mjsonfmt:\033[0m \033[0;91mAn error occurred!\033[0m\n")


if __name__ == "__main__":
    unittest.main()
