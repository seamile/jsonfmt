#!/usr/bin/env python
'''JSON Formatter'''

import io
import json
import os
import sys
from argparse import ArgumentParser
from collections import OrderedDict
from functools import partial
from pydoc import pager
from shutil import get_terminal_size
from tempfile import NamedTemporaryFile, _TemporaryFileWrapper
from typing import IO, Any, Callable, List, Optional, Sequence, Tuple, Union
from unittest.mock import patch

import pyperclip
import toml
import yaml
from jmespath import compile as parse_jmespath
from jmespath.exceptions import JMESPathError
from jmespath.parser import ParsedResult as JMESPath
from jsonpath_ng import JSONPath
from jsonpath_ng import parse as parse_jsonpath
from jsonpath_ng.exceptions import JSONPathError
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, TOMLLexer, YamlLexer

from . import __version__
from .diff import compare
from .utils import exit_with_error, load_value, print_err, print_inf

QueryPath = Union[JMESPath, JSONPath]
TEMP_CLIPBOARD = io.StringIO()


class FormatError(Exception):
    pass


def is_clipboard_available() -> bool:
    '''check if the clipboard available'''
    copy_fn, paste_fn = pyperclip.determine_clipboard()
    return copy_fn.__class__.__name__ != 'ClipboardUnavailable' \
        and paste_fn.__class__.__name__ != 'ClipboardUnavailable'


def parse_querypath(querypath: Optional[str], querylang: Optional[str]):
    '''parse the querypath'''
    if querypath is None:
        return None
    elif querylang is None:
        parsers = [parse_jmespath, parse_jsonpath]
    elif querylang in ['jmespath', 'jsonpath']:
        parsers = [{'jmespath': parse_jmespath, 'jsonpath': parse_jsonpath}[querylang]]
    else:
        exit_with_error(f'invalid querylang: "{querylang}"')

    for parse in parsers:
        try:
            return parse(querypath)
        except (JMESPathError, JSONPathError, AttributeError):
            pass

    exit_with_error(f'invalid querypath expression: "{querypath}"')


def extract_elements(qpath: QueryPath, py_obj: Any) -> Any:
    '''find and extract elements via JMESPath or JSONPath'''
    if isinstance(qpath, JMESPath):
        return qpath.search(py_obj)
    else:
        items = [matched.value for matched in qpath.find(py_obj)]
        n_items = len(items)
        if n_items == 0:
            return None
        elif n_items == 1:
            return items[0]
        else:
            return items


def parse_to_pyobj(text: str, qpath: Optional[QueryPath]) -> Tuple[Any, str]:
    '''read json, toml or yaml from IO and then match sub-element by jmespath'''
    # parse json, toml or yaml to python object
    loads_methods: dict[str, Callable] = {
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
        raise FormatError("no json, toml or yaml found in the text")

    if qpath is None:
        return py_obj, fmt
    else:
        # match sub-elements via jmespath or jsonpath
        return extract_elements(qpath, py_obj), fmt


def traverse_to_bottom(py_obj: Any, keys: str) -> Tuple[Any, Union[str, int]]:
    '''traverse the nested py_obj to bottom by keys'''
    def key_or_idx(obj: Any, key: str):
        '''return str for dict and int for list'''
        return int(key) if isinstance(obj, list) else key

    # make sure the keys joined by `.`, and then split
    _keys = keys.replace(']', '').replace('[', '.').split('.')

    for k in _keys[:-1]:
        py_obj = py_obj[key_or_idx(py_obj, k)]

    return py_obj, key_or_idx(py_obj, _keys[-1])


def sort_dict(py_obj: Any) -> Any:
    '''sort the dicts in py_obj by keys'''
    if isinstance(py_obj, dict):
        sorted_items = sorted((key, sort_dict(value)) for key, value in py_obj.items())
        return OrderedDict(sorted_items)
    elif isinstance(py_obj, list):
        return [sort_dict(item) for item in py_obj]
    else:
        return py_obj


def modify_pyobj(py_obj: Any, sets: List[str], pops: List[str]):
    '''add, modify or pop items for PyObj'''
    for kv in sets:
        try:
            keys, value = kv.split('=')
            bottom, last_k = traverse_to_bottom(py_obj, keys)
            if isinstance(bottom, list) and len(bottom) <= last_k:  # type: ignore
                bottom.append(load_value(value))
            else:
                bottom[last_k] = load_value(value)  # type: ignore
        except (IndexError, KeyError, ValueError, TypeError):
            print_err(f'invalid key path: {kv}')
            continue

    for keys in pops:
        try:
            bottom, last_k = traverse_to_bottom(py_obj, keys)
            bottom.pop(last_k)
        except (IndexError, KeyError):
            print_err(f'invalid key path: {keys}')
            continue


def get_overview(py_obj: Any) -> Any:
    '''extract the structure of the data'''
    def clip(value: Any) -> Any:
        if isinstance(value, str):
            return '...'
        elif isinstance(value, (list, tuple)):
            return []
        elif isinstance(value, dict):
            return {k: clip(v) for k, v in value.items()}
        else:
            return value

    if isinstance(py_obj, list) and len(py_obj) > 1:
        return [clip(py_obj[0])]
    else:
        return clip(py_obj)


def format_to_text(py_obj: Any, fmt: str, *,
                   compact: bool, escape: bool,
                   indent: str, sort_keys: bool) -> str:
    '''format the py_obj to text'''
    if fmt == 'json':
        if compact:
            result = json.dumps(py_obj, ensure_ascii=escape, sort_keys=sort_keys,
                                separators=(',', ':'))
        else:
            result = json.dumps(py_obj, ensure_ascii=escape, sort_keys=sort_keys,
                                indent='\t' if indent == 't' else int(indent))
    elif fmt == 'toml':
        if not isinstance(py_obj, dict):
            msg = 'the pyobj must be a Mapping when format to toml'
            raise FormatError(msg)
        result = toml.dumps(sort_dict(py_obj) if sort_keys else py_obj)
    elif fmt == 'yaml':
        _indent = None if indent == 't' else int(indent)
        result = yaml.safe_dump(py_obj, allow_unicode=not escape, indent=_indent,
                                sort_keys=sort_keys)
    else:
        raise FormatError('Unknow format')

    return result.strip() + '\n'


def get_output_fp(input_file: IO, cp2clip: bool, diff: bool,
                  overview: bool, overwrite: bool, del_tmpfile=True) -> IO:
    if cp2clip:
        return TEMP_CLIPBOARD
    elif diff:
        name = f"_{os.path.basename(input_file.name)}"
        return NamedTemporaryFile(mode='w+', prefix='jf-', suffix=name,
                                  delete=del_tmpfile, delete_on_close=False)
    elif input_file is sys.stdin or overview:
        return sys.stdout
    elif overwrite:
        return input_file
    else:
        return sys.stdout


def output(output_fp: IO, text: str, fmt: str):
    if hasattr(output_fp, 'name') and output_fp.name == '<stdout>':
        if output_fp.isatty():
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
            output_fp.write(text)
    elif isinstance(output_fp, (io.TextIOWrapper, _TemporaryFileWrapper)):
        # For regular files, changes the position to the beginning
        # and truncates the file to zero length before overwriting
        output_fp.seek(0)
        output_fp.truncate()
        output_fp.write(text)
        output_fp.close()
        print_inf(f'result written to {os.path.basename(output_fp.name)}')
    elif isinstance(output_fp, io.StringIO) and output_fp.tell() != 0:
        output_fp.write('\n\n')
        output_fp.write(text)
    else:
        output_fp.write(text)


def process(input_fp: IO, qpath: Optional[QueryPath], to_fmt: Optional[str], *,
            compact: bool, escape: bool, indent: str, overview: bool,
            sort_keys: bool, sets: Optional[list], pops: Optional[list]):
    # parse and format
    input_text = input_fp.read()
    py_obj, fmt = parse_to_pyobj(input_text, qpath)

    if sets or pops:
        modify_pyobj(py_obj, sets, pops)  # type: ignore

    if overview:
        py_obj = get_overview(py_obj)

    to_fmt = to_fmt or fmt
    formated_text = format_to_text(py_obj, to_fmt,
                                   compact=compact, escape=escape,
                                   indent=indent, sort_keys=sort_keys)
    return formated_text, to_fmt


def parse_cmdline_args() -> ArgumentParser:
    parser = ArgumentParser('jsonfmt')

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('-C', dest='cp2clip', action='store_true',
                      help='CopyMode, which will copy the processing result to the clipboard')
    mode.add_argument('-d', dest='diff', action='store_true',
                      help='DiffMode, which compares the difference between the two input data')
    mode.add_argument('-D', dest='difftool', type=str,
                      help='DifftoolMode, similar to "DiffMode". You can specify a tool to perform diff comparisons')
    mode.add_argument('-o', dest='overview', action='store_true',
                      help='OverviewMode, which can display an overview of the structure of the data')
    mode.add_argument('-O', dest='overwrite', action='store_true',
                      help='OverwriteMode, which will overwrite the original file with the formated text')

    parser.add_argument('-c', dest='compact', action='store_true',
                        help='Suppress all whitespace separation (most compact), only valid for JSON')
    parser.add_argument('-e', dest='escape', action='store_true',
                        help='escape non-ASCII characters')
    parser.add_argument('-f', dest='format', choices=['json', 'toml', 'yaml'],
                        help='the format to output (default: same as input)')
    parser.add_argument('-i', dest='indent', metavar='{0-8 or t}',
                        choices='012345678t', default='2',
                        help='number of spaces for indentation (default: %(default)s)')
    parser.add_argument('-l', dest='querylang', choices=['jmespath', 'jsonpath'],
                        help='query language for extracting data (default: auto-detect)')
    parser.add_argument('-p', dest='querypath', type=str,
                        help='the path for querying')
    parser.add_argument('-s', dest='sort_keys', action='store_true',
                        help='sort the output of dictionaries alphabetically by key')
    parser.add_argument('--set', metavar="'foo.k1=v1;k2[i]=v2'",
                        help='key-value pairs to add or modify (seperated by `;`)')
    parser.add_argument('--pop', metavar="'k1;foo.k2;k3[i]'",
                        help='key-value pairs to delete (seperated by `;`)')
    parser.add_argument(dest='files', nargs='*',
                        help='the files that will be processed')
    parser.add_argument('-v', dest='version', action='version',
                        version=__version__, help="show the version")
    return parser


def main(_args: Optional[Sequence[str]] = None):
    parser = parse_cmdline_args()
    args = parser.parse_args(_args)

    # check and parse the querypath
    querypath = parse_querypath(args.querypath, args.querylang)

    # check if the clipboard is available
    if args.cp2clip and not is_clipboard_available():
        exit_with_error('clipboard is not available')

    # check the input files
    files = args.files or [sys.stdin]
    n_files = len(files)
    if n_files < 1:
        exit_with_error('no data file specified')

    # check the diff mode
    diff_mode: bool = args.diff or args.difftool
    if diff_mode and len(files) != 2:
        exit_with_error('less than two files')
    sort_keys = True if diff_mode else args.sort_keys
    del_tmpfile = False if args.difftool == 'code' else True

    # get sets and pops
    sets = [k.strip() for k in args.set.split(';')] if args.set else []
    pops = [k.strip() for k in args.pop.split(';')] if args.pop else []

    output_title = n_files > 1 and not (diff_mode or args.cp2clip or args.overwrite)

    diff_files = []
    for idx, file in enumerate(files, start=1):
        if output_title:
            title = f'{idx}. {file}' if idx == 1 else f'\n{idx}. {file}'
            print(f'\033[37m{title}\033[0m')

        try:
            # process the input data file
            input_fp = open(file, 'r+') if isinstance(file, str) else file
            formated, fmt = process(input_fp, querypath, args.format,
                                    compact=args.compact, escape=args.escape,
                                    indent=args.indent, overview=args.overview,
                                    sort_keys=sort_keys, sets=sets, pops=pops)
            # output the result
            output_fp = get_output_fp(input_fp, args.cp2clip, diff_mode,
                                      args.overview, args.overwrite, del_tmpfile)

            output(output_fp, formated, fmt)
            if args.diff or args.difftool:
                diff_files.append(output_fp)
        except (FormatError, JMESPathError, JSONPathError) as err:
            exit_with_error(err)
        except FileNotFoundError:
            exit_with_error(f'no such file: {file}')
        except PermissionError:
            exit_with_error(f'permission denied: {file}')
        except KeyboardInterrupt:
            exit_with_error('user canceled')

        finally:
            input_fp = locals().get('input_fp')
            if isinstance(input_fp, io.TextIOBase):
                input_fp.close()

    if args.cp2clip:
        TEMP_CLIPBOARD.seek(0)
        pyperclip.copy(TEMP_CLIPBOARD.read())
        print_inf('result copied to clipboard')
    elif diff_mode:
        try:
            path1, path2 = [f.name for f in diff_files]
            compare(path1, path2, args.difftool)
        except (OSError, ValueError) as err:
            exit_with_error(err)


if __name__ == "__main__":
    main()
