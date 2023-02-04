#!/usr/bin/env python
import json
import sys

json_files = sys.argv[1:]

for f_json in json_files:
    with open(f_json, 'r+') as fp:
        try:
            j_data = json.load(fp)
        except Exception:
            print(f"{f_json} is not a json file")
        else:
            fp.seek(0)
            fp.truncate()
            json.dump(j_data, fp, ensure_ascii=False, sort_keys=True, indent=4)
