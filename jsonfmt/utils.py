import sys
from ast import literal_eval
from collections import OrderedDict
from typing import Any


def safe_eval(value: str) -> Any:
    '''Safely evaluates the provided string expression as a Python literal'''
    try:
        return literal_eval(value)
    except (ValueError, SyntaxError):
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
