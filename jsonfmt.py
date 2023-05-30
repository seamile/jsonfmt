#!/usr/bin/env python
'''JSON Format Tool'''

import json
import pyperclip
import toml
import yaml
from argparse import ArgumentParser
from functools import partial
from jsonpath import jsonpath
from pydoc import pager
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer, TOMLLexer, YamlLexer
from shutil import get_terminal_size
from sys import stdin, stdout, stderr, exit
from typing import Any, IO, Optional, Sequence

__version__ = '0.2.4'


def print_inf(msg: Any):
    print(f'\033[1;94mjsonfmt:\033[0m \033[0;94m{msg}\033[0m', file=stdout)


def print_err(msg: Any):
    print(f'\033[1;91mjsonfmt:\033[0m \033[0;91m{msg}\033[0m', file=stderr)


class ParseError(Exception):
    pass


def is_clipboard_available() -> bool:
    copy_fn, paste_fn = pyperclip.determine_clipboard()
    return copy_fn.__class__.__name__ != 'ClipboardUnavailable' \
        and paste_fn.__class__.__name__ != 'ClipboardUnavailable'


def parse_to_pyobj(input_fp: IO, jpath: Optional[str]) -> Any:
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
        raise ParseError(f"no json, toml or yaml object in `{input_fp.name}`")

    if jpath is None:
        return py_obj
    else:
        # match sub-elements via jsonpath
        subelements = jsonpath(py_obj, jpath)
        if subelements is False:
            raise ParseError('wrong jsonpath')
        else:
            return subelements


def output(output_fp: IO, text: str, text_format: str, cp2clip: bool):
    # copy the result to clipboard
    if cp2clip:
        pyperclip.copy(text)
        print_inf('result copied to clipboard.')
        return
    elif output_fp.isatty():
        # highlight the text when output to TTY divice
        Lexer = {
            'json': JsonLexer,
            'toml': TOMLLexer,
            'yaml': YamlLexer,
        }[text_format]
        colored_text = highlight(text, Lexer(), TerminalFormatter())
        t_width, t_hight = get_terminal_size()
        if text.count('\n') >= t_hight or len(text) > t_width * (t_hight - 1):
            pager(colored_text)
        else:
            output_fp.write(colored_text)
    else:
        output_fp.write(text)


def output_json(py_obj: Any, output_fp: IO, *,
                cp2clip: bool, compact: bool, escape: bool, indent: int):
    '''output formated json to file or stdout'''
    if compact:
        json_text = json.dumps(py_obj, ensure_ascii=escape, sort_keys=True,
                               separators=(',', ':'))
    else:
        json_text = json.dumps(py_obj, ensure_ascii=escape, sort_keys=True,
                               indent=indent)

    # append a blank line at the end of `fp`
    if json_text[-1] != '\n':
        json_text += '\n'

    output(output_fp, json_text, 'json', cp2clip)


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

    output(output_fp, toml_text, 'toml', cp2clip)


def output_yaml(py_obj: Any, output_fp: IO, *,
                cp2clip: bool, escape: bool, indent: int):
    '''output formated yaml to file or stdout'''
    yaml_text = yaml.safe_dump(py_obj, allow_unicode=not escape, indent=indent,
                               sort_keys=True)

    # copy the result to clipboard
    if cp2clip:
        pyperclip.copy(yaml_text)
        print_inf('result copied to clipboard.')
        return

    output(output_fp, yaml_text, 'yaml', cp2clip)


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
    parser.add_argument('-p', dest='jsonpath', type=str,
                        help='output part of the object via jsonpath')
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

    # match the specified output function
    fn_output = {
        'json': partial(output_json, cp2clip=cp2clip, compact=args.compact,
                        escape=args.escape, indent=args.indent),
        'yaml': partial(output_yaml, cp2clip=cp2clip, escape=args.escape,
                        indent=args.indent),
        'toml': partial(output_toml, cp2clip=cp2clip),
    }[args.format]

    if args.files:
        for file in args.files:
            try:
                # read from file
                with open(file, 'r+') as input_fp:
                    try:
                        py_obj = parse_to_pyobj(input_fp, args.jsonpath)
                    except ParseError as err:
                        print_err(err)
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
        except ParseError as err:
            print_err(err)
            exit(2)
        else:
            fn_output(py_obj, stdout)


if __name__ == "__main__":
    main()
