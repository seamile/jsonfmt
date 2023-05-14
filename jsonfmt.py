#!/usr/bin/env python
'''JSON Format Tool'''

import json
from sys import stdin, stdout, stderr
from argparse import ArgumentParser
from typing import Any, List, IO, Optional, Sequence, Union

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

__version__ = '0.1.4'


def print_err(msg: str):
    print(f'\033[0;91m{msg}\033[0m', file=stderr)


class JSONPathError(Exception):
    pass


def parse_jsonpath(jsonpath: str) -> List[Union[str, int]]:
    '''parse the jsonpath into a list of pathname components'''
    jsonpath = jsonpath.strip().strip('/')
    if not jsonpath:
        return []
    else:
        components = jsonpath.split('/')
        for i, c in enumerate(components):
            if c.isdecimal():
                components[i] = int(c)  # type: ignore
        return components  # type: ignore


def match_element(py_obj: Any, jpath_components: List[Union[str, int]]) -> Any:
    for i, c in enumerate(jpath_components):
        if c == '*' and isinstance(py_obj, list):
            return [match_element(sub_obj, jpath_components[i + 1:])
                    for sub_obj in py_obj]
        else:
            try:
                py_obj = py_obj[c]
            except (IndexError, KeyError, TypeError):
                raise JSONPathError(f'Invalid path node `{c}`')

    return py_obj


def read_json_to_py(json_fp: IO, jsonpath: str) -> Any:
    '''read json obj from IO and match sub-element by jsonpath'''
    # parse json object to python object
    try:
        py_obj = json.load(json_fp)
    except (json.JSONDecodeError, UnicodeDecodeError):
        print_err(f"no json object found from `{json_fp.name}`")
        return

    # parse jsonpath and match the sub-element of py_obj
    jpath_components = parse_jsonpath(jsonpath)
    try:
        return match_element(py_obj, jpath_components)
    except JSONPathError as e:
        print_err(f'{e}')
        return


def output(py_obj: Any, compact: bool, escape: bool, indent: int,
           output_fp: IO = stdout):
    '''output formated json to file or stdout'''
    if output_fp.fileno() > 2:
        output_fp.seek(0)
        output_fp.truncate()

    if compact:
        json_text = json.dumps(py_obj, ensure_ascii=escape, sort_keys=True,
                               separators=(',', ':'))
    else:
        json_text = json.dumps(py_obj, ensure_ascii=escape, sort_keys=True,
                               indent=indent)

    # highlight the json code when outputint to TTY divice
    if output_fp.isatty():
        json_text = highlight(json_text, JsonLexer(), TerminalFormatter())

    # append a blank line at the end of `fp``
    if json_text[-1] != '\n':
        json_text += '\n'

    output_fp.write(json_text)


def parse_cmdline_args(args: Optional[Sequence[str]] = None):
    parser = ArgumentParser('jsonfmt')
    parser.add_argument('-c', dest='compression', action='store_true',
                        help='compression the json object in the files or stdin')
    parser.add_argument('-e', dest='escape', action='store_true',
                        help='escape non-ASCII characters')
    parser.add_argument('-i', dest='indent', type=int, default=4,
                        help='number of spaces to use for indentation (default: %(default)s)')
    parser.add_argument('-O', dest='overwrite', action='store_true',
                        help='overwrite the formated json object into the json file')
    parser.add_argument('-p', dest='jsonpath', type=str, default='',
                        help='output part of json object via jsonpath')
    parser.add_argument(dest='json_files', nargs='*',
                        help='the json files that will be processed')
    parser.add_argument('-v', dest='version', action='version', version=__version__,
                        help="show the version")
    return parser.parse_args(args)


def main():
    args = parse_cmdline_args()

    if args.json_files:
        for j_file in args.json_files:
            try:
                # read json from file
                with open(j_file, 'r+') as json_fp:
                    if py_obj := read_json_to_py(json_fp, args.jsonpath):
                        output_fp = json_fp if args.overwrite else stdout
                        output(py_obj, args.compression, args.escape,
                               args.indent, output_fp)
            except FileNotFoundError:
                print_err(f'No such file `{j_file}`')
    else:
        # read json from stdin
        if py_obj := read_json_to_py(stdin, args.jsonpath):
            output(py_obj, args.compression, args.escape, args.indent)


if __name__ == "__main__":
    main()
