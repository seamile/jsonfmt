#!/usr/bin/env python
'''JSON Format Tool'''

import json
import pyperclip
import re
import toml
import yaml
from argparse import ArgumentParser
from functools import partial
from io import TextIOBase
from jsonpath import jsonpath
from pydoc import pager
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, TOMLLexer, YamlLexer
from shutil import get_terminal_size
from sys import stdin, stdout, stderr
from typing import Any, List, IO, Optional, Sequence, Tuple, Union
from unittest.mock import patch

__version__ = '0.2.4'

NUMERIC = re.compile(r'-?\d+$|-?\d+\.\d+$|^-?\d+\.?\d+e-?\d+$')
DICT_OR_LIST = re.compile(r'^\{.*\}$|^\[.*\]$')


def print_inf(msg: Any):
    print(f'\033[1;94mjsonfmt:\033[0m \033[0;94m{msg}\033[0m', file=stderr)


def print_err(msg: Any):
    print(f'\033[1;91mjsonfmt:\033[0m \033[0;91m{msg}\033[0m', file=stderr)


class ParseError(Exception):
    pass


class JsonPathError(Exception):
    pass


def is_clipboard_available() -> bool:
    '''check if the clipboard available'''
    copy_fn, paste_fn = pyperclip.determine_clipboard()
    return copy_fn.__class__.__name__ != 'ClipboardUnavailable' \
        and paste_fn.__class__.__name__ != 'ClipboardUnavailable'


def parse_to_pyobj(text: str, jpath: Optional[str]) -> Tuple[Any, str]:
    '''read json, toml or yaml from IO and then match sub-element by jsonpath'''
    # parse json, toml or yaml to python object
    loads_methods = {
        'json': json.loads,
        'toml': toml.loads,
        'yaml': partial(yaml.load, Loader=yaml.Loader),
    }

    # try to load the text to be parsed
    for fmt, fn_loads in loads_methods.items():
        try:
            py_obj = fn_loads(text)
            break
        except Exception:
            continue
    else:
        raise ParseError("no json, toml or yaml found in the text")

    if jpath is None:
        return py_obj, fmt
    else:
        # match sub-elements via jsonpath
        subelements = jsonpath(py_obj, jpath)
        if subelements is False:
            raise JsonPathError('invalid JSONPath or query result is empty')
        else:
            return subelements, fmt


def forward_by_keys(py_obj: Any, keys: str) -> Tuple[Any, Union[str, int]]:
    next_k = lambda obj, k: int(k) if isinstance(obj, list) else k

    _keys = keys.replace(']', '').replace('[', '.').split('.')
    for k in _keys[:-1]:
        py_obj = py_obj[next_k(py_obj, k)]
    else:
        return py_obj, next_k(py_obj, _keys[-1])


def load_value(value: str):
    if NUMERIC.match(value):
        return eval(value)
    elif DICT_OR_LIST.match(value):
        try:
            return eval(value)
        except Exception:
            return value
    else:
        return value


def modify_pyobj(py_obj: Any, sets: List[str], pops: List[str]):
    for kv in sets:
        try:
            keys, value = kv.split('=')
            bottom, last_k = forward_by_keys(py_obj, keys)
            bottom[last_k] = load_value(value)
        except (IndexError, KeyError, ValueError):
            print_err(f'invalid key path: {kv}')
            continue

    for keys in pops:
        try:
            bottom, last_k = forward_by_keys(py_obj, keys)
            bottom.pop(last_k)
        except (IndexError, KeyError):
            print_err(f'invalid key path: {keys}')
            continue


def get_overview(py_obj: Any):
    def clip_value(value: Any):
        if isinstance(value, str):
            return '...'
        elif isinstance(value, (list, tuple)):
            return []
        elif isinstance(value, dict):
            return {k: clip_value(v) for k, v in value.items()}
        else:
            return value

    if isinstance(py_obj, list):
        return [clip_value(py_obj[0])]
    else:
        return clip_value(py_obj)


def format_to_text(py_obj: Any, fmt: str, *,
                   compact: bool, escape: bool,
                   indent: Union[int, str], sort_keys: bool) -> str:
    '''format the py_obj to text'''
    if fmt == 'json':
        if compact:
            return json.dumps(py_obj, ensure_ascii=escape, sort_keys=sort_keys,
                              separators=(',', ':'))
        else:
            return json.dumps(py_obj, ensure_ascii=escape, sort_keys=sort_keys,
                              indent=indent)

    elif fmt == 'toml':
        if not isinstance(py_obj, dict):
            msg = 'the pyobj must be a Mapping when format to toml'
            raise ParseError(msg)
        return toml.dumps(py_obj)

    elif fmt == 'yaml':
        _indent = None if indent == '\t' else int(indent)
        return yaml.safe_dump(py_obj, allow_unicode=not escape, indent=_indent,
                              sort_keys=sort_keys)

    else:
        raise ParseError('Unknow format')


def output(output_fp: IO, text: str, fmt: str, cp2clip: bool):
    # copy the result to clipboard
    if cp2clip:
        pyperclip.copy(text)
        print_inf('result copied to clipboard.')
        return
    elif output_fp.isatty():
        # highlight the text when output to TTY divice
        Lexer = {'json': JsonLexer, 'toml': TOMLLexer, 'yaml': YamlLexer}[fmt]
        colored_text = highlight(text, Lexer(), TerminalFormatter())
        win_w, win_h = get_terminal_size()
        # use pager when line-hight > screen hight or
        if text.count('\n') >= win_h or len(text) > win_w * (win_h - 1):
            with patch("sys.stdin.isatty", lambda *_: True):
                pager(colored_text)
        else:
            output_fp.write(colored_text)
    else:
        output_fp.seek(0)
        output_fp.truncate()
        output_fp.write(text)
        if output_fp.fileno() > 2:
            print_inf(f'result written to {output_fp.name}.')


def process(input_fp: IO, jpath: Optional[str], convert_fmt: Optional[str], *,
            compact: bool, cp2clip: bool, escape: bool, indent: Union[int, str],
            overview: bool, overwrite: bool, sort_keys: bool,
            sets: Optional[list], pops: Optional[list]):
    # parse and format
    input_text = input_fp.read()
    py_obj, fmt = parse_to_pyobj(input_text, jpath)

    if sets or pops:
        modify_pyobj(py_obj, sets, pops)  # type: ignore

    if overview:
        py_obj = get_overview(py_obj)

    convert_fmt = convert_fmt or fmt
    formated_text = format_to_text(py_obj, convert_fmt,
                                   compact=compact, escape=escape,
                                   indent=indent, sort_keys=sort_keys)

    # output the result
    if input_fp.name == '<stdin>' or not overwrite:
        output_fp = stdout
    else:
        # truncate file to zero length before overwrite
        output_fp = input_fp
    output(output_fp, formated_text, convert_fmt, cp2clip)


def parse_cmdline_args(args: Optional[Sequence[str]] = None):
    parser = ArgumentParser('jsonfmt')
    parser.add_argument('-c', dest='compact', action='store_true',
                        help='suppress all whitespace separation')
    parser.add_argument('-C', dest='cp2clip', action='store_true',
                        help='copy the result to clipboard')
    parser.add_argument('-e', dest='escape', action='store_true',
                        help='escape non-ASCII characters')
    parser.add_argument('-f', dest='format', choices=['json', 'toml', 'yaml'],
                        help='the format to output ''(default: %(default)s)')
    parser.add_argument('-i', dest='indent', metavar='{0-8,t}',
                        choices='012345678t', default='2',
                        help='number of spaces for indentation (default: %(default)s)')
    parser.add_argument('-o', dest='overview', action='store_true',
                        help='show data structure overview')
    parser.add_argument('-O', dest='overwrite', action='store_true',
                        help='overwrite the formated text to original file')
    parser.add_argument('-p', dest='jsonpath', type=str,
                        help='output part of the object via jsonpath')
    parser.add_argument('-s', dest='sort_keys', action='store_true',
                        help='sort keys of objects on output')
    parser.add_argument('--set', metavar="'foo.k1=v1;k2[i]=v2'",
                        help='set the keys to values (seperated by `;`)')
    parser.add_argument('--pop', metavar="'k1;foo.k2;k3[i]'",
                        help='pop the specified keys (seperated by `;`)')
    parser.add_argument(dest='files', nargs='*',
                        help='the files that will be processed')
    parser.add_argument('-v', dest='version', action='version',
                        version=__version__, help="show the version")
    return parser.parse_args(args)


def main():
    args = parse_cmdline_args()

    # check if the clipboard is available
    cp2clip = args.cp2clip and is_clipboard_available()
    if args.cp2clip and not cp2clip:
        print_err('clipboard unavailable')

    # check the indent
    indent = '\t' if args.indent == 't' else int(args.indent)

    # the overwrite will be forced to close when showing overview
    overwrite = False if args.overview else args.overwrite

    # get sets and pops
    sets = [k.strip() for k in args.set.split(';')] if args.set else []
    pops = [k.strip() for k in args.pop.split(';')] if args.pop else []

    files = args.files or [stdin]

    for file in files:
        try:
            # read from file
            input_fp = open(file, 'r+') if isinstance(file, str) else file
            process(input_fp,
                    args.jsonpath,
                    args.format,
                    compact=args.compact,
                    cp2clip=cp2clip,
                    escape=args.escape,
                    indent=indent,
                    overview=args.overview,
                    overwrite=overwrite,
                    sort_keys=args.sort_keys,
                    sets=sets,
                    pops=pops)
        except ParseError as err:
            print_err(err)
        except FileNotFoundError:
            print_err(f'no such file `{file}`')
        finally:
            input_fp = locals().get('input_fp')
            if isinstance(input_fp, TextIOBase):
                input_fp.close()


if __name__ == "__main__":
    main()
