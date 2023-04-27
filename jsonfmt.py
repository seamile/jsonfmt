#!/usr/bin/env python
'''JSON Format Tool'''

import json
from sys import stdin
from argparse import ArgumentParser
from typing import Any, Optional, IO

__version__ = '0.1.1'


def print_err(msg: str):
    print(f'\033[0;31m{msg}\033[0m')


class JSONPathError(Exception):
    pass


def output(json_obj: Any, output_fp: Optional[IO] = None, compression: bool = False):
    '''output formated json to file or stdout'''
    if output_fp is None:
        if compression:
            j_str = json.dumps(json_obj, ensure_ascii=False,
                               sort_keys=True, separators=(',', ':'))
        else:
            j_str = json.dumps(json_obj, ensure_ascii=False,
                               sort_keys=True, indent=4)
        print(j_str)
    else:
        output_fp.seek(0)
        output_fp.truncate()
        if compression:
            json.dump(json_obj, output_fp, ensure_ascii=False,
                      sort_keys=True, separators=(',', ':'))
        else:
            json.dump(json_obj, output_fp, ensure_ascii=False,
                      sort_keys=True, indent=4)


def parse_jsonpath(jsonpath: str) -> list[str | int]:
    jsonpath = jsonpath.strip().strip('/')
    if not jsonpath:
        return []
    else:
        components = jsonpath.split('/')
        for i, c in enumerate(components):
            if c.isdecimal():
                components[i] = int(c)  # type: ignore
        return components  # type: ignore


def get_element_by_components(json_obj: Any, jpath_components: list[str | int]) -> Any:
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


def main():
    parser = ArgumentParser('jsonfmt')
    parser.add_argument('-c', dest='compression', action='store_true',
                        help='compression the json object in the files or stdin.')
    parser.add_argument('-O', dest='overwrite', action='store_true',
                        help='overwrite the formated json object into the json file.')
    parser.add_argument('-p', dest='jsonpath', type=str, default='',
                        help='output part of json object via jsonpath.')
    parser.add_argument(dest='json_files', nargs='*',
                        help='the json files that will be processed')
    parser.add_argument('-v', dest='version', action='version', version=__version__,
                        help="show the version.")
    args = parser.parse_args()

    if args.json_files:
        # get json from files
        for j_file in args.json_files:
            try:
                with open(j_file, 'r+') as fp:
                    try:
                        j_obj = json.load(fp)
                        matched_obj = jsonpath_match(j_obj, args.jsonpath)
                    except json.decoder.JSONDecodeError:
                        print_err(f"File `{j_file}` does not contains JSON string")
                        continue
                    except JSONPathError as e:
                        print_err(f'{e}')
                        continue
                    output_fp = fp if args.overwrite else None
                    output(matched_obj, output_fp, args.compression)

            except FileNotFoundError:
                print_err(f'No such file `{j_file}`')
    else:
        # get json from stdin
        try:
            j_obj = json.load(stdin)
            matched_obj = jsonpath_match(j_obj, args.jsonpath)
        except json.decoder.JSONDecodeError:
            print_err('Wrong JSON format')
            exit(1)
        except JSONPathError as e:
            print_err(f'{e}')
            exit(2)
        else:
            output(matched_obj, None, args.compression)


if __name__ == "__main__":
    main()
