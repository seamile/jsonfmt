import os
from shutil import which
from subprocess import PIPE, STDOUT, call, run

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import DiffLexer

from .utils import print_inf


def cmp_by_diff(path1: str, path2: str):
    """use diff to compare the difference between two files"""
    result = run(['diff', '-u', '--', path1, path2], stdout=PIPE, stderr=STDOUT, text=True)
    if result.returncode == 0:
        print_inf('no difference')
    else:
        output = highlight(result.stdout.rstrip('\n'), DiffLexer(), TerminalFormatter())
        print(output)


def cmp_by_fc(path1: str, path2: str):
    """use fc to compare the difference between two files"""
    fc = os.path.join(os.environ['WINDIR'], 'system32', 'fc.exe')
    call([fc, '/n', path1, path2])


def cmp_by_code(path1: str, path2: str):
    """use VS Code to compare the difference between two files"""
    call(['code', '--diff', path1, path2])


def cmp_by_git(path1: str, path2: str):
    """use Git to compare the difference between two files"""
    result = run(['git', 'config', '--global', 'diff.tool'], stdout=PIPE, stderr=STDOUT, text=True)
    if result.returncode == 0:
        cmp_by_others(result.stdout.strip(), path1, path2)
    else:
        call(['git', 'diff', '--color=always', '--no-index', path1, path2])


def cmp_by_others(difftool: str, path1: str, path2: str):
    """compare the differences between two files by other tools"""
    if ' ' in difftool:
        command = [*difftool.split(), path1, path2]
    else:
        command = [difftool, path1, path2]
    call(command)


def has_command(command: str) -> bool:
    """check if the command is valid"""
    if os.name not in ('posix', 'nt'):
        raise OSError('unsupported operating system')
    return which(command.split()[0]) is not None


def compare(path1: str, path2: str, difftool: str | None = None):
    """compare the differences between two files"""
    if difftool is None:
        support_tools = ['git', 'code', 'kdiff3', 'meld', 'vimdiff', 'diff', 'WinMerge', 'fc']
        # find a difftool available on OS
        for difftool in support_tools:
            if has_command(difftool):
                break
        else:
            raise ValueError('not found any available difftool')

    if difftool == 'git':
        cmp_by_git(path1, path2)
    elif difftool == 'code':
        cmp_by_code(path1, path2)
    elif difftool == 'diff':
        cmp_by_diff(path1, path2)
    elif difftool == 'fc':
        cmp_by_fc(path1, path2)
    else:
        cmp_by_others(difftool, path1, path2)
