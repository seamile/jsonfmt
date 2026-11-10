import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from jsonfmt import jsonfmt


class UndecodableInputTestCase(unittest.TestCase):
    """Files that cannot be text-decoded must report a clean error."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.bad_file = str(Path(self.tmp.name) / 'bad.json')
        with open(self.bad_file, 'wb') as fp:
            fp.write(b'{"k": "\x81"}')

    def test_undecodable_file_no_traceback(self):
        err = StringIO()
        with patch.multiple(
            sys, argv=['jf', self.bad_file], stdout=StringIO(), stderr=err
        ):
            jsonfmt.main()  # must not raise
        self.assertIn('codec', err.getvalue().lower())

    def test_undecodable_file_merge_mode(self):
        good_file = str(Path(self.tmp.name) / 'good.json')
        with open(good_file, 'w', encoding='utf-8') as fp:
            fp.write('{"a": 1}')
        err = StringIO()
        with (
            patch.multiple(
                sys,
                argv=['jf', '-m', good_file, self.bad_file],
                stdout=StringIO(),
                stderr=err,
            ),
            self.assertRaises(SystemExit),
        ):
            jsonfmt.main()
        self.assertIn('codec', err.getvalue().lower())
