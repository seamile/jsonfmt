import re

NUMERIC = re.compile(r'-?\d+$|-?\d+\.\d+$|^-?\d+\.?\d+e-?\d+$')
DICT_OR_LIST = re.compile(r'^\{.*\}$|^\[.*\]$')


def load_value(value: str):
    if NUMERIC.match(value):
        return eval(value)
    elif DICT_OR_LIST.match(value):
        try:
            return eval(value)
        except Exception:
            return value
    else:
        return value
