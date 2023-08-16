import re
from sys import stderr
from typing import Any

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


def print_inf(msg: Any):
    print(f'\033[1;94mjsonfmt:\033[0m \033[0;94m{msg}\033[0m', file=stderr)


def print_err(msg: Any):
    print(f'\033[1;91mjsonfmt:\033[0m \033[0;91m{msg}\033[0m', file=stderr)
