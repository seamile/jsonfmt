import os
from subprocess import call, getstatusoutput
from typing import Optional

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import DiffLexer

from .utils import print_err


def cmp_by_diff(path1: str, path2: str):
    '''use diff to compare the difference between two files'''
    stat, result = getstatusoutput(f'diff -u {path1} {path2}')
    if stat == 0:
        print_err(result)
    else:
        output = highlight(result, DiffLexer(), TerminalFormatter())
        print(output)


def cmp_by_fc(path1: str, path2: str):
    '''use fc to compare the difference between two files'''
    fc = os.path.join(os.environ["WINDIR"], 'system32', 'fc.exe')
    call([fc, '/n', path1, path2])


def cmp_by_code(path1: str, path2: str):
    '''use VS Code to compare the difference between two files'''
    call(['code', '--diff', path1, path2])


def cmp_by_git(path1: str, path2: str):
    '''use Git to compare the difference between two files'''
    stat, cmd = getstatusoutput('git config --global diff.tool')
    if stat == 0:
        cmp_by_others(cmd, path1, path2)
    else:
        call(['git', 'diff', '--color=always', '--no-index', path1, path2])


def cmp_by_others(difftool: str, path1: str, path2: str):
    '''compare the differences between two files by other tools'''
    if ' ' in difftool:
        command = difftool.split() + [path1, path2]
    else:
        command = [difftool, path1, path2]
    call(command)


def has_command(command: str) -> bool:
    '''check if the command is valid'''
    _cmd = command.split()[0]
    if os.name == 'posix':
        return os.system(f'hash {_cmd} > /dev/null 2>&1') == 0
    elif os.name == 'nt':
        return os.system(f'where {_cmd}') == 0
    else:
        raise OSError('unsupported operating system')


def compare(path1: str, path2: str, difftool: Optional[str] = None):
    '''compare the differences between two files'''
    if difftool is None:
        support_tools = ['git', 'code', 'kdiff3', 'meld', 'vimdiff', 'diff',
                         'WinMerge', 'fc']
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
