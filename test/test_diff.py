import os
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
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
        with patch.multiple(df, call=self.mock_call), patch.dict(os.environ, {'WINDIR': 'c'}):
            df.cmp_by_fc('file1.txt', 'file2.txt')
        self.mock_call.assert_called_once_with([str(Path('c') / 'system32' / 'fc.exe'), '/n', 'file1.txt', 'file2.txt'])

    def test_cmp_by_code(self):
        with patch.multiple(df, call=self.mock_call):
            df.cmp_by_code('file1.txt', 'file2.txt')
        self.mock_call.assert_called_once_with(['code', '--diff', 'file1.txt', 'file2.txt'])

    def test_cmp_by_git(self):

        self.mock_run.return_value = Mock(returncode=0, stdout='vimdiff\n')
        with patch.multiple(df, call=self.mock_call, run=self.mock_run):
            df.cmp_by_git('file1.txt', 'file2.txt')
        self.mock_call.assert_called_once_with(['vimdiff', 'file1.txt', 'file2.txt'])
        self.mock_run.assert_called_once_with(
            ['git', 'config', '--global', 'diff.tool'], stdout=df.PIPE, stderr=df.STDOUT, text=True
        )

        self.mock_call.reset_mock()
        self.mock_run.reset_mock()
        self.mock_run.return_value = Mock(returncode=1, stdout='')
        with patch.multiple(df, call=self.mock_call, run=self.mock_run):
            df.cmp_by_git('file1.txt', 'file2.txt')
        self.mock_call.assert_called_once_with(
            ['git', 'diff', '--color=always', '--no-index', 'file1.txt', 'file2.txt']
        )

    def test_cmp_by_others(self):
        with patch.multiple(df, call=self.mock_call):
            df.cmp_by_others('foo --bar', 'file1.txt', 'file2.txt')
        self.mock_call.assert_called_once_with(['foo', '--bar', 'file1.txt', 'file2.txt'])

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

    def test_compare_explicit_tools(self):
        comparators = ('cmp_by_git', 'cmp_by_code', 'cmp_by_diff', 'cmp_by_fc', 'cmp_by_others')
        cases = {
            'git': 'cmp_by_git',
            'code': 'cmp_by_code',
            'diff': 'cmp_by_diff',
            'fc': 'cmp_by_fc',
            'custom-tool': 'cmp_by_others',
        }

        for difftool, expected in cases.items():
            mocks = {name: Mock() for name in comparators}
            with self.subTest(difftool=difftool), patch.multiple(df, **mocks):
                df.compare('file1.txt', 'file2.txt', difftool)

            if expected == 'cmp_by_others':
                mocks[expected].assert_called_once_with(difftool, 'file1.txt', 'file2.txt')
            else:
                mocks[expected].assert_called_once_with('file1.txt', 'file2.txt')
            for name, comparator in mocks.items():
                if name != expected:
                    comparator.assert_not_called()

    def test_compare_auto_selects_available_tool(self):
        comparators = ('cmp_by_git', 'cmp_by_code', 'cmp_by_diff', 'cmp_by_fc', 'cmp_by_others')
        mocks = {name: Mock() for name in comparators}
        with (
            patch.object(df, 'has_command', side_effect=lambda command: command == 'code'),
            patch.multiple(df, **mocks),
        ):
            df.compare('file1.txt', 'file2.txt')

        mocks['cmp_by_code'].assert_called_once_with('file1.txt', 'file2.txt')
        for name, comparator in mocks.items():
            if name != 'cmp_by_code':
                comparator.assert_not_called()

    def test_compare_without_available_tool(self):
        with patch.object(df, 'has_command', return_value=False), self.assertRaises(ValueError):
            df.compare('file1.txt', 'file2.txt')
