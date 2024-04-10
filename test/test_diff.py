import os
import sys
import unittest
from unittest.mock import Mock, patch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from jsonfmt import diff as df


class TestDiff(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_call = Mock()
        self.mock_getstatusoutput = Mock()
        self.mock_system = Mock()

    def test_cmp_by_diff(self):

        self.mock_getstatusoutput.return_value = (0, '')
        with patch.multiple(df, getstatusoutput=self.mock_getstatusoutput):
            df.cmp_by_diff('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_getstatusoutput.called)
        self.assertEqual(self.mock_getstatusoutput.call_args[0][0],
                         'diff -u file1.txt file2.txt')

        self.mock_getstatusoutput.return_value = (1, '')
        with patch.multiple(df, getstatusoutput=self.mock_getstatusoutput):
            df.cmp_by_diff('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_getstatusoutput.called)

    def test_cmp_by_fc(self):
        with patch.multiple(df, call=self.mock_call):
            os.environ["WINDIR"] = 'c'
            df.cmp_by_fc('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(self.mock_call.call_args[0][0][1:], ['/n', 'file1.txt', 'file2.txt'])

    def test_cmp_by_code(self):
        with patch.multiple(df, call=self.mock_call):
            df.cmp_by_code('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(self.mock_call.call_args[0][0], ['code', '--diff', 'file1.txt', 'file2.txt'])

    def test_cmp_by_git(self):

        self.mock_getstatusoutput.return_value = (0, 'vimdiff')
        with patch.multiple(df, call=self.mock_call, getstatusoutput=self.mock_getstatusoutput):
            df.cmp_by_git('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(self.mock_call.call_args[0][0], ['vimdiff', 'file1.txt', 'file2.txt'])

        self.mock_getstatusoutput.return_value = (1, '')
        with patch.multiple(df, call=self.mock_call, getstatusoutput=self.mock_getstatusoutput):
            df.cmp_by_git('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(self.mock_call.call_args[0][0],
                         ['git', 'diff', '--color=always', '--no-index', 'file1.txt', 'file2.txt'])

    def test_cmp_by_others(self):
        with patch.multiple(df, call=self.mock_call):
            df.cmp_by_others('foo --bar', 'file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(self.mock_call.call_args[0][0],
                         ['foo', '--bar', 'file1.txt', 'file2.txt'])

    @patch('os.name', 'posix')
    def test_has_command_posix(self):
        self.mock_system.return_value = 0
        with patch('os.system', self.mock_system):
            for cmd in ['ls', 'pwd', 'cat']:
                self.assertTrue(df.has_command(cmd))
                self.assertEqual(self.mock_system.call_args[0][0], f'hash {cmd} > /dev/null 2>&1')

    @patch('os.name', 'nt')
    def test_has_command_nt(self):
        self.mock_system.return_value = 0
        with patch('os.system', self.mock_system):
            for cmd in ['dir', 'cd', 'type']:
                self.assertTrue(df.has_command(cmd))
                self.assertEqual(self.mock_system.call_args[0][0], f'where {cmd}')

    @patch('os.name', 'unsupported_os')
    def test_has_command_unsupported_os(self):
        with self.assertRaises(OSError):
            df.has_command('ls')

    @patch('os.name', 'posix')
    def test_command_not_found(self):
        self.mock_system.return_value = 1
        with patch('os.system', self.mock_system):
            for command in ['nonexistent_command', 'invalid_command']:
                self.assertFalse(df.has_command(command))

    @patch('os.name', 'posix')
    def test_compare(self):
        tools = [None, 'git', 'code', 'diff', 'fc', 'unknow-diff-tool']
        self.mock_system.return_value = 0
        for tool in tools:
            with patch.multiple(df, call=self.mock_call), patch('os.system', self.mock_system):
                df.compare('file1.txt', 'file2.txt', tool)
            self.assertTrue(self.mock_call.called)

        self.mock_system.return_value = 1
        with patch('os.system', self.mock_system), self.assertRaises(ValueError):
            df.compare('file1.txt', 'file2.txt', None)
