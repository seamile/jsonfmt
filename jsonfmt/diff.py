import os
from subprocess import call, getstatusoutput
from typing import Optional

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import DiffLexer

from .utils import print_err


def cmp_by_diff(path1: str, path2: str):
    '''use diff to compare the difference between two files'''
    stat, result = getstatusoutput(f'diff -h {path1} {path2}')
    if stat == 0:
        output = highlight(result, DiffLexer(), TerminalFormatter())
        print(output)
    else:
        print_err(result)


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


def cmp_by_others(cmd: str, path1: str, path2: str):
    '''compare the differences between two files by other tools'''
    call([cmd, path1, path2])


def has_command(command) -> bool:
    '''check if the command is valid'''
    if os.name == 'posix':
        return os.system(f'hash {command} > /dev/null 2>&1') == 0
    elif os.name == 'nt':
        return os.system(f'where {command}') == 0
    else:
        raise OSError('unsupported operating system')


def compare(path1: str, path2: str, tool: Optional[str] = None):
    '''compare the differences between two files'''
    if tool is None:
        support_tools = ['git', 'code', 'kdiff3', 'meld', 'vimdiff', 'diff',
                         'winmergeu', 'fc']
        # find a difftool available on OS
        for tool in support_tools:
            if has_command(tool):
                break
        else:
            raise ValueError('not found any available difftool')

    if tool == 'git':
        cmp_by_git(path1, path2)
    elif tool == 'code':
        cmp_by_code(path1, path2)
    elif tool == 'diff':
        cmp_by_diff(path1, path2)
    elif tool == 'fc':
        cmp_by_fc(path1, path2)
    else:
        call([tool, path1, path2])
