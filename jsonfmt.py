#!/usr/bin/env python
'''JSON Format Tool'''

import json
from sys import stdin
from argparse import ArgumentParser

parser = ArgumentParser('jsonfmt')
parser.add_argument('-c', dest='compression', action='store_true',
                    help='compression the jsonfiles.')
parser.add_argument('-o', dest='output_std', action='store_true',
                    help='only output the result to `stdout`.')
parser.add_argument(dest='json_files', nargs='*',
                    help='the json files that will be processed')
args = parser.parse_args()


def print_err(msg):
    print(f'\033[0;31m{msg}\033[0m')


def main():
    if args.json_files:
        # get json from files
        for j_file in args.json_files:
            try:
                with open(j_file, 'r+') as fp:
                    try:
                        j_obj = json.load(fp)
                    except json.decoder.JSONDecodeError:
                        print_err(f"File `{j_file}` does not contains JSON string")
                        continue

                    if args.output_std:
                        if args.compression:
                            j_str = json.dumps(j_obj, ensure_ascii=False,
                                               sort_keys=True, separators=(',', ':'))
                        else:
                            j_str = json.dumps(j_obj, ensure_ascii=False,
                                               sort_keys=True, indent=4)
                        print(j_str)
                    else:
                        fp.seek(0)
                        fp.truncate()
                        if args.compression:
                            json.dump(j_obj, fp, ensure_ascii=False,
                                      sort_keys=True, separators=(',', ':'))
                        else:
                            json.dump(j_obj, fp, ensure_ascii=False,
                                      sort_keys=True, indent=4)
            except FileNotFoundError:
                print_err(f'No such file `{j_file}`')
    else:
        # get json from stdin
        try:
            j_obj = json.load(stdin)  # type: ignore
        except json.decoder.JSONDecodeError:
            print_err('Wrong JSON format')
            exit(1)
        else:
            if args.compression:
                j_str = json.dumps(j_obj, ensure_ascii=False,
                                   sort_keys=True, separators=(',', ':'))
            else:
                j_str = json.dumps(j_obj, ensure_ascii=False,
                                   sort_keys=True, indent=4)
            print(j_str)


if __name__ == "__main__":
    main()
