import re
import sys
from typing import Any
from collections import OrderedDict

NUMERIC = re.compile(r'-?\d+$|-?\d+\.\d+$|^-?\d+\.?\d+e-?\d+$')
DICT_OR_LIST = re.compile(r'^\{.*\}$|^\[.*\]$')


def load_value(value: str) -> Any:
    if NUMERIC.match(value):
        return eval(value)
    elif DICT_OR_LIST.match(value):
        try:
            return eval(value)
        except Exception:
            return value
    else:
        return value


def sort_dict(py_obj: Any) -> Any:
    '''sort the dicts in py_obj by keys'''
    if isinstance(py_obj, dict):
        sorted_items = sorted((key, sort_dict(value)) for key, value in py_obj.items())
        return OrderedDict(sorted_items)
    elif isinstance(py_obj, list):
        return [sort_dict(item) for item in py_obj]
    else:
        return py_obj


def print_inf(msg: Any):
    print(f'\033[0;94m{msg}\033[0m', file=sys.stderr)


def print_err(msg: Any):
    print(f'\033[1;91mjsonfmt:\033[0m \033[0;91m{msg}\033[0m', file=sys.stderr)


def exit_with_error(err_msg):
    print_err(err_msg)
    sys.exit(1)
