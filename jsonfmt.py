#!/usr/bin/env python
'''JSON Format Tool'''

import json
import tomlkit
import yaml

from argparse import ArgumentParser
from functools import partial
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, YamlLexer, TOMLLexer
from sys import stdin, stdout, stderr, exit
from typing import Any, List, IO, Optional, Sequence, Union

__version__ = '0.2.0'


def print_err(msg: str):
    print(f'\033[1;91mjsonfmt:\033[0m \033[0;91m{msg}\033[0m', file=stderr)


class JSONPathError(Exception):
    pass


class JSONParseError(Exception):
    pass


def parse_jsonpath(jsonpath: str) -> List[Union[str, int]]:
    '''parse the jsonpath into a list of pathname components'''
    if jsonpath := jsonpath.strip().strip('/'):
        components = jsonpath.split('/')
        for i, component in enumerate(components):
            if component.isdecimal():
                components[i] = int(component)  # type: ignore
        return components  # type: ignore
    else:
        return []


def match_element(py_obj: Any, jpath_components: List[Union[str, int]]) -> Any:
    for i, component in enumerate(jpath_components):
        if component == '*' and isinstance(py_obj, list):
            return [match_element(sub_obj, jpath_components[i + 1:])
                    for sub_obj in py_obj]
        else:
            try:
                py_obj = py_obj[component]
            except (IndexError, KeyError, TypeError) as err:
                raise JSONPathError(f'invalid path node `{component}`') from err

    return py_obj


def read_json_to_py(json_fp: IO, jsonpath: str) -> Any:
    '''read json obj from IO and match sub-element by jsonpath'''
    # parse json object to python object
    try:
        py_obj = json.load(json_fp)
    except (json.JSONDecodeError, UnicodeDecodeError) as err:
        print_err(f"no json object in `{json_fp.name}`")
        raise JSONParseError from err

    # parse jsonpath and match the sub-element of py_obj
    jpath_components = parse_jsonpath(jsonpath)
    try:
        return match_element(py_obj, jpath_components)
    except JSONPathError as err:
        print_err(f'{err}')
        raise JSONParseError from err


def output_json(py_obj: Any, compact: bool, escape: bool, indent: int,
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

    # highlight the json code when output to TTY divice
    if output_fp.isatty():
        json_text = highlight(json_text, JsonLexer(), TerminalFormatter())

    # append a blank line at the end of `fp``
    if json_text[-1] != '\n':
        json_text += '\n'

    output_fp.write(json_text)


def output_yaml(py_obj: Any, output_fp: IO = stdout):
    '''output formated yaml to file or stdout'''
    if output_fp.fileno() > 2:
        output_fp.seek(0)
        output_fp.truncate()

    # highlight the json code when output to TTY divice
    if output_fp.isatty():
        yaml_text = yaml.safe_dump(py_obj, allow_unicode=True, sort_keys=True)
        highlight_yaml = highlight(yaml_text, YamlLexer(), TerminalFormatter())
        output_fp.write(highlight_yaml)
    else:
        yaml.safe_dump(py_obj, output_fp, allow_unicode=True, sort_keys=True)


def output_toml(py_obj: Any, output_fp: IO = stdout):
    '''output formated toml to file or stdout'''
    if output_fp.fileno() > 2:
        output_fp.seek(0)
        output_fp.truncate()

    toml_text = tomlkit.dumps(py_obj, sort_keys=True)

    # highlight the json code when output to TTY divice
    if output_fp.isatty():
        toml_text = highlight(toml_text, TOMLLexer(), TerminalFormatter())

    output_fp.write(toml_text)


def parse_cmdline_args(args: Optional[Sequence[str]] = None):
    parser = ArgumentParser('jsonfmt')
    parser.add_argument('-c', dest='compact', action='store_true',
                        help='compact the json object to a single line')
    parser.add_argument('-e', dest='escape', action='store_true',
                        help='escape non-ASCII characters')
    parser.add_argument('-f', dest='format', choices=['json', 'toml', 'yaml'],
                        default='json', help='the format to output (default: %(default)s)')
    parser.add_argument('-i', dest='indent', type=int, default=4,
                        help='number of spaces to use for indentation (default: %(default)s)')
    parser.add_argument('-O', dest='overwrite', action='store_true',
                        help='overwrite the formated json object to original file')
    parser.add_argument('-p', dest='jsonpath', type=str, default='',
                        help='output part of json object via jsonpath')
    parser.add_argument(dest='json_files', nargs='*',
                        help='the json files that will be processed')
    parser.add_argument('-v', dest='version', action='version',
                        version=__version__, help="show the version")
    return parser.parse_args(args)


def main():
    args = parse_cmdline_args()

    # match the specified output function
    output_func = {
        'json': partial(output_json, compact=args.compact, escape=args.escape, indent=args.indent),
        'yaml': output_yaml,
        'toml': output_toml,
    }[args.format]

    if args.json_files:
        for j_file in args.json_files:
            try:
                # read json from file
                with open(j_file, 'r+') as json_fp:
                    try:
                        py_obj = read_json_to_py(json_fp, args.jsonpath)
                    except JSONParseError:
                        exit(1)
                    else:
                        output_fp = json_fp if args.overwrite else stdout
                        output_func(py_obj, output_fp=output_fp)
            except FileNotFoundError:
                print_err(f'no such file `{j_file}`')
    else:
        # read json from stdin
        try:
            py_obj = read_json_to_py(stdin, args.jsonpath)
        except JSONParseError:
            exit(1)
        else:
            output_func(py_obj, output_fp=stdout)


if __name__ == "__main__":
    main()
