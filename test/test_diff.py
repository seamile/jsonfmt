import os
import sys
import unittest
from unittest.mock import Mock, patch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
from jsonfmt import diff as df  # noqa: E402 -- Add the repository to sys.path before importing.


class TestDiff(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_call = Mock()
        self.mock_run = Mock(return_value=Mock(returncode=0, stdout=''))
        self.mock_which = Mock(return_value='/bin/git')

    def test_cmp_by_diff(self):

        with patch.multiple(df, run=self.mock_run):
            df.cmp_by_diff('file1.txt', 'file2.txt')
        self.mock_run.assert_called_once_with(
            ['diff', '-u', '--', 'file1.txt', 'file2.txt'], stdout=df.PIPE, stderr=df.STDOUT, text=True
        )

        self.mock_run.return_value = Mock(returncode=1, stdout='difference\n')
        with patch.multiple(df, run=self.mock_run), patch('builtins.print') as output:
            df.cmp_by_diff('file one; echo unsafe.txt', '-file2.txt')
        self.assertEqual(
            self.mock_run.call_args.args[0], ['diff', '-u', '--', 'file one; echo unsafe.txt', '-file2.txt']
        )
        output.assert_called_once()

    def test_cmp_by_fc(self):
        with patch.multiple(df, call=self.mock_call):
            os.environ['WINDIR'] = 'c'
            df.cmp_by_fc('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(self.mock_call.call_args[0][0][1:], ['/n', 'file1.txt', 'file2.txt'])

    def test_cmp_by_code(self):
        with patch.multiple(df, call=self.mock_call):
            df.cmp_by_code('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(self.mock_call.call_args[0][0], ['code', '--diff', 'file1.txt', 'file2.txt'])

    def test_cmp_by_git(self):

        self.mock_run.return_value = Mock(returncode=0, stdout='vimdiff\n')
        with patch.multiple(df, call=self.mock_call, run=self.mock_run):
            df.cmp_by_git('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(self.mock_call.call_args[0][0], ['vimdiff', 'file1.txt', 'file2.txt'])
        self.mock_run.assert_called_once_with(
            ['git', 'config', '--global', 'diff.tool'], stdout=df.PIPE, stderr=df.STDOUT, text=True
        )

        self.mock_run.return_value = Mock(returncode=1, stdout='')
        with patch.multiple(df, call=self.mock_call, run=self.mock_run):
            df.cmp_by_git('file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(
            self.mock_call.call_args[0][0], ['git', 'diff', '--color=always', '--no-index', 'file1.txt', 'file2.txt']
        )

    def test_cmp_by_others(self):
        with patch.multiple(df, call=self.mock_call):
            df.cmp_by_others('foo --bar', 'file1.txt', 'file2.txt')
        self.assertTrue(self.mock_call.called)
        self.assertEqual(self.mock_call.call_args[0][0], ['foo', '--bar', 'file1.txt', 'file2.txt'])

    @patch('os.name', 'posix')
    def test_has_command_posix(self):
        with patch.object(df, 'which', self.mock_which):
            for cmd in ['ls', 'pwd', 'cat']:
                self.assertTrue(df.has_command(cmd))
                self.mock_which.assert_called_with(cmd)

    @patch('os.name', 'nt')
    def test_has_command_nt(self):
        with patch.object(df, 'which', self.mock_which):
            for cmd in ['git', 'code', 'fc']:
                self.assertTrue(df.has_command(cmd))
                self.mock_which.assert_called_with(cmd)

    @patch('os.name', 'unsupported_os')
    def test_has_command_unsupported_os(self):
        with self.assertRaises(OSError):
            df.has_command('ls')

    @patch('os.name', 'posix')
    def test_command_not_found(self):
        self.mock_which.return_value = None
        with patch.object(df, 'which', self.mock_which):
            for command in ['nonexistent_command', 'invalid_command']:
                self.assertFalse(df.has_command(command))

    @patch('os.name', 'posix')
    def test_compare(self):
        tools = [None, 'git', 'code', 'diff', 'fc', 'unknow-diff-tool']
        for tool in tools:
            self.mock_call.reset_mock()
            self.mock_run.reset_mock()
            with patch.multiple(df, call=self.mock_call, run=self.mock_run, which=self.mock_which):
                df.compare('file1.txt', 'file2.txt', tool)
            self.assertTrue(self.mock_call.called or self.mock_run.called)

        self.mock_which.return_value = None
        with patch.object(df, 'which', self.mock_which), self.assertRaises(ValueError):
            df.compare('file1.txt', 'file2.txt', None)
