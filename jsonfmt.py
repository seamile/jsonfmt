#!/usr/bin/env python
'''JSON Format Tool'''

import json
import tomlkit
import yaml
from tomlkit.exceptions import UnexpectedCharError
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


class ParseError(Exception):
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


def parse_to_pyobj(input_fp: IO, jsonpath: str) -> Any:
    '''read json, yaml or toml from IO and then match sub-element by jsonpath'''
    # parse json, yaml or toml to python object
    yaml_load = partial(yaml.load, Loader=yaml.Loader)
    for fn_load in [json.load, tomlkit.load, yaml_load]:
        if input_fp.fileno() > 2:
            input_fp.seek(0)
        try:
            py_obj = fn_load(input_fp)
            break
        except (json.JSONDecodeError, UnicodeDecodeError, UnexpectedCharError):
            continue
    else:
        print_err(f"no json object in `{input_fp.name}`")
        exit(1)

    # parse jsonpath and match the sub-element of py_obj
    jpath_components = parse_jsonpath(jsonpath)
    try:
        return match_element(py_obj, jpath_components)
    except JSONPathError as err:
        print_err(f'{err}')
        raise ParseError from err


def output_json(py_obj: Any, output_fp: IO, compact: bool,
                escape: bool, indent: int):
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


def output_yaml(py_obj: Any, output_fp: IO, escape: bool, indent: int):
    '''output formated yaml to file or stdout'''
    if output_fp.fileno() > 2:
        output_fp.seek(0)
        output_fp.truncate()

    # highlight the json code when output to TTY divice
    if output_fp.isatty():
        yaml_text = yaml.safe_dump(py_obj, allow_unicode=not escape,
                                   indent=indent, sort_keys=True)
        highlight_yaml = highlight(yaml_text, YamlLexer(), TerminalFormatter())
        output_fp.write(highlight_yaml)
    else:
        yaml.safe_dump(py_obj, output_fp, allow_unicode=not escape,
                       indent=indent, sort_keys=True)


def output_toml(py_obj: Any, output_fp: IO):
    '''output formated toml to file or stdout'''
    if not isinstance(py_obj, dict):
        print_err('the pyobj must be a Mapping when format to toml')
        exit(1)

    if output_fp.fileno() > 2:
        output_fp.seek(0)
        output_fp.truncate()

    # highlight the json code when output to TTY divice
    if output_fp.isatty():
        toml_text = tomlkit.dumps(py_obj, sort_keys=True)
        highlight_toml = highlight(toml_text, TOMLLexer(), TerminalFormatter())
        output_fp.write(highlight_toml)
    else:
        tomlkit.dump(py_obj, output_fp, sort_keys=True)


def parse_cmdline_args(args: Optional[Sequence[str]] = None):
    parser = ArgumentParser('jsonfmt')
    parser.add_argument('-c', dest='compact', action='store_true',
                        help='compact the json object to a single line')
    parser.add_argument('-e', dest='escape', action='store_true',
                        help='escape non-ASCII characters')
    parser.add_argument('-f', dest='format', choices=['json', 'toml', 'yaml'],
                        default='json', help='the format to output (default: %(default)s)')
    parser.add_argument('-i', dest='indent', type=int, default=2,
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
    fn_output = {
        'json': partial(output_json, compact=args.compact,
                        escape=args.escape, indent=args.indent),
        'yaml': partial(output_yaml, escape=args.escape, indent=args.indent),
        'toml': output_toml,
    }[args.format]

    if args.json_files:
        for j_file in args.json_files:
            try:
                # read from file
                with open(j_file, 'r+') as input_fp:
                    try:
                        py_obj = parse_to_pyobj(input_fp, args.jsonpath)
                    except ParseError:
                        exit(1)
                    else:
                        output_fp = input_fp if args.overwrite else stdout
                        fn_output(py_obj, output_fp)
            except FileNotFoundError:
                print_err(f'no such file `{j_file}`')
    else:
        # read from stdin
        try:
            py_obj = parse_to_pyobj(stdin, args.jsonpath)
        except ParseError:
            exit(1)
        else:
            fn_output(py_obj, stdout)


if __name__ == "__main__":
    main()
