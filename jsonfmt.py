#!/usr/bin/env python
'''JSON Format Tool'''

import json
import pyperclip
import toml
import yaml
from argparse import ArgumentParser
from functools import partial
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, TOMLLexer, YamlLexer
from sys import stdin, stdout, stderr, exit
from typing import Any, List, IO, Optional, Sequence, Union

__version__ = '0.2.1'


def print_inf(msg: str):
    print(f'\033[1;94mjsonfmt:\033[0m \033[0;94m{msg}\033[0m')


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
    '''read json, toml or yaml from IO and then match sub-element by jsonpath'''
    # parse json, toml or yaml to python object
    obj_text = input_fp.read()
    yaml_load = partial(yaml.load, Loader=yaml.Loader)
    for fn_loads in [json.loads, toml.loads, yaml_load]:
        try:
            py_obj = fn_loads(obj_text)
            break
        except Exception:
            continue
    else:
        print_err(f"no json, toml or yaml object in `{input_fp.name}`")
        raise ParseError

    # parse jsonpath and match the sub-element of py_obj
    jpath_components = parse_jsonpath(jsonpath)
    try:
        return match_element(py_obj, jpath_components)
    except JSONPathError as err:
        print_err(f'{err}')
        raise ParseError from err


def output_json(py_obj: Any, output_fp: IO, *, cp2clip: bool, compact: bool,
                escape: bool, indent: int):
    '''output formated json to file or stdout'''
    if compact:
        json_text = json.dumps(py_obj, ensure_ascii=escape, sort_keys=True,
                               separators=(',', ':'))
    else:
        json_text = json.dumps(py_obj, ensure_ascii=escape, sort_keys=True,
                               indent=indent)

    # copy the result to clipboard
    if cp2clip:
        pyperclip.copy(json_text)
        print_inf('result copied to clipboard.')
        return

    # highlight the json code when output to TTY divice
    if output_fp.isatty():
        json_text = highlight(json_text, JsonLexer(), TerminalFormatter())

    # append a blank line at the end of `fp`
    if json_text[-1] != '\n':
        json_text += '\n'

    output_fp.write(json_text)


def output_toml(py_obj: Any, output_fp: IO, *, cp2clip: bool):
    '''output formated toml to file or stdout'''
    if not isinstance(py_obj, dict):
        print_err('the pyobj must be a Mapping when format to toml')
        exit(3)

    toml_text = toml.dumps(py_obj)

    # copy the result to clipboard
    if cp2clip:
        pyperclip.copy(toml_text)
        print_inf('result copied to clipboard.')
        return

    # highlight the toml code when output to TTY divice
    if output_fp.isatty():
        toml_text = highlight(toml_text, TOMLLexer(), TerminalFormatter())

    output_fp.write(toml_text)


def output_yaml(py_obj: Any, output_fp: IO, *, cp2clip: bool, escape: bool, indent: int):
    '''output formated yaml to file or stdout'''
    yaml_text = yaml.safe_dump(py_obj, allow_unicode=not escape, indent=indent,
                               sort_keys=True)

    # copy the result to clipboard
    if cp2clip:
        pyperclip.copy(yaml_text)
        print_inf('result copied to clipboard.')
        return

    # highlight the yaml code when output to TTY divice
    if output_fp.isatty():
        yaml_text = highlight(yaml_text, YamlLexer(), TerminalFormatter())

    output_fp.write(yaml_text)


def parse_cmdline_args(args: Optional[Sequence[str]] = None):
    parser = ArgumentParser('jsonfmt')
    parser.add_argument('-c', dest='compact', action='store_true',
                        help='compact the json object to a single line')
    parser.add_argument('-C', dest='cp2clip', action='store_true',
                        help='copy the result to clipboard')
    parser.add_argument('-e', dest='escape', action='store_true',
                        help='escape non-ASCII characters')
    parser.add_argument('-f', dest='format', default='json',
                        choices=['json', 'toml', 'yaml'],
                        help='the format to output ''(default: %(default)s)')
    parser.add_argument('-i', dest='indent', type=int, default=2,
                        help='number of spaces for indentation (default: %(default)s)')
    parser.add_argument('-O', dest='overwrite', action='store_true',
                        help='overwrite the formated text to original file')
    parser.add_argument('-p', dest='jsonpath', type=str, default='',
                        help='output part of the object via jsonpath')
    parser.add_argument(dest='files', nargs='*',
                        help='the files that will be processed')
    parser.add_argument('-v', dest='version', action='version',
                        version=__version__, help="show the version")
    return parser.parse_args(args)


def main():
    args = parse_cmdline_args()

    # match the specified output function
    fn_output = {
        'json': partial(output_json, cp2clip=args.cp2clip, compact=args.compact,
                        escape=args.escape, indent=args.indent),
        'yaml': partial(output_yaml, cp2clip=args.cp2clip, escape=args.escape, indent=args.indent),
        'toml': partial(output_toml, cp2clip=args.cp2clip),
    }[args.format]

    if args.files:
        for file in args.files:
            try:
                # read from file
                with open(file, 'r+') as input_fp:
                    try:
                        py_obj = parse_to_pyobj(input_fp, args.jsonpath)
                    except ParseError:
                        exit(1)
                    else:
                        if args.overwrite:
                            # truncate file to zero length before overwrite
                            input_fp.seek(0)
                            input_fp.truncate()
                            output_fp = input_fp
                        else:
                            output_fp = stdout

                        fn_output(py_obj, output_fp)
            except FileNotFoundError:
                print_err(f'no such file `{file}`')
    else:
        try:
            # read from stdin
            py_obj = parse_to_pyobj(stdin, args.jsonpath)
        except ParseError:
            exit(2)
        else:
            fn_output(py_obj, stdout)


if __name__ == "__main__":
    main()
