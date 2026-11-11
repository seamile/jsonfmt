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
        Path(self.bad_file).write_bytes(b'{"k": "\x81"}')

    def test_undecodable_file_no_traceback(self):
        err = StringIO()
        with patch.multiple(sys, argv=['jf', self.bad_file], stdout=StringIO(), stderr=err):
            jsonfmt.main()
        self.assertIn('codec', err.getvalue().lower())

    def test_undecodable_file_merge_mode(self):
        good_file = str(Path(self.tmp.name) / 'good.json')
        Path(good_file).write_text('{"a": 1}', encoding='utf-8')
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
