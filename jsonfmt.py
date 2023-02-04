#!/usr/bin/env python
'''JSON Format Tool'''

import json
from argparse import ArgumentParser

parser = ArgumentParser('jsonfmt')
parser.add_argument('-c', dest='compression', action='store_true',
                    help='compression the jsonfiles.')
parser.add_argument('-o', dest='output_std', action='store_true',
                    help='only output the result to `stdout`.')
parser.add_argument(dest='json_files', nargs='+',
                    help='the json files that will be processed')
args = parser.parse_args()


for j_file in args.json_files:
    try:
        with open(j_file, 'r+') as fp:
            try:
                j_obj = json.load(fp)
            except Exception:
                print(f"{j_file} is not a json file")
                continue

            if args.output_std:
                if args.compression:
                    j_str = json.dumps(j_obj, ensure_ascii=False, separators=(',', ':'))
                else:
                    j_str = json.dumps(j_obj, ensure_ascii=False, sort_keys=True, indent=4)
                print(j_str)
            else:
                fp.seek(0)
                fp.truncate()
                if args.compression:
                    json.dump(j_obj, fp, ensure_ascii=False, separators=(',', ':'))
                else:
                    json.dump(j_obj, fp, ensure_ascii=False, sort_keys=True, indent=4)
    except FileNotFoundError:
        print(f'no such file: {j_file}')
