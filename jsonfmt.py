#!/usr/bin/env python
'''JSON Format Tool'''

import json
from sys import stdin, stdout, stderr
from argparse import ArgumentParser
from typing import Any, List, IO, Union

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

__version__ = '0.1.3'


def print_err(msg: str):
    print(f'\033[0;31m{msg}\033[0m', file=stderr)


class JSONPathError(Exception):
    pass


def output(json_obj: Any, compression: bool, escape: bool, indent: int,
           output_fp: IO = stdout):
    '''output formated json to file or stdout'''
    if output_fp.fileno() > 2:
        output_fp.seek(0)
        output_fp.truncate()
    if compression:
        json.dump(json_obj, output_fp, ensure_ascii=escape,
                  sort_keys=True, separators=(',', ':'))
    else:
        json_text = json.dumps(json_obj, ensure_ascii=escape,
                               sort_keys=True, indent=indent)
        # highlight the json code when outputint to TTY divice
        if output_fp.isatty():
            json_text = highlight(json_text, JsonLexer(), TerminalFormatter())
        output_fp.write(json_text)

    # append a blank line at the end of `fp``
    output_fp.write('\n')


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


def get_element_by_components(json_obj: Any,
                              jpath_components: List[Union[str, int]]) -> Any:
    for i, c in enumerate(jpath_components):
        if c == '*' and isinstance(json_obj, list):
            return [get_element_by_components(sub_obj, jpath_components[i + 1:])
                    for sub_obj in json_obj]
        else:
            try:
                json_obj = json_obj[c]
            except (IndexError, KeyError, TypeError):
                raise JSONPathError(f'Invalid path node `{c}`')

    return json_obj


def jsonpath_match(json_obj: Any, jsonpath: str) -> Any:
    jpath_components = parse_jsonpath(jsonpath)
    if not jpath_components:
        return json_obj
    else:
        return get_element_by_components(json_obj, jpath_components)


def parse_cmdline_args():
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
    return parser.parse_args()


def main():
    args = parse_cmdline_args()

    if args.json_files:
        # get json from files
        for j_file in args.json_files:
            try:
                with open(j_file, 'r+') as fp:
                    try:
                        j_obj = json.load(fp)
                        matched_obj = jsonpath_match(j_obj, args.jsonpath)
                    except json.decoder.JSONDecodeError:
                        print_err(f"no json object found from file `{j_file}`")
                        continue
                    except JSONPathError as e:
                        print_err(f'{e}')
                        continue
                    output_fp = fp if args.overwrite else stdout
                    output(matched_obj, args.compression, args.escape,
                           args.indent, output_fp)

            except FileNotFoundError:
                print_err(f'No such file `{j_file}`')
    else:
        # get json from stdin
        try:
            j_obj = json.load(stdin)
            matched_obj = jsonpath_match(j_obj, args.jsonpath)
        except json.decoder.JSONDecodeError:
            print_err("no json object found from `stdin`")
            exit(1)
        except JSONPathError as e:
            print_err(f'{e}')
            exit(2)
        else:
            output(matched_obj, args.compression, args.escape, args.indent)


if __name__ == "__main__":
    main()
