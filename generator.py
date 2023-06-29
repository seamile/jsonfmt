'''
Generate class from py_dict for languages

TODO:
    Markups:
        XML, CSV
    Languages:
        C, Cpp, Csharp, Dart, Go, Java, Javascript, Kotlin,
        ObjectiveC, Php, Python, Ruby, Rust, Swift, Typescript
    Databases:
        MySQL, PostgreSQL, MS-SQL, SQLite3
    ORMs:
        Django, Sqlalchemy, Spring, others
'''

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, List, Optional


TEMPLATE_C = ''
TEMPLATE_CPP = ''
TEMPLATE_CSHARP = ''
TEMPLATE_DART = ''
TEMPLATE_GO = ''
TEMPLATE_JAVA = ''
TEMPLATE_JAVASCRIPT = ''
TEMPLATE_KOTLIN = ''
TEMPLATE_OBJECTIVEC = ''
TEMPLATE_PHP = ''
TEMPLATE_PYTHON = ''
TEMPLATE_RUBY = ''
TEMPLATE_RUST = ''
TEMPLATE_SWIFT = ''
TEMPLATE_TYPESCRIPT = ''


class Type(StrEnum):
    null = 'null'
    boolean = 'boolean'
    integer = 'int'
    decimal = 'float'
    string = 'string'
    date = 'date'
    datetime = 'datetime'
    array = 'array'
    vector = 'vector'
    mapping = 'mapping'


@dataclass
class Field:
    name: str
    ftype: Type


@dataclass
class Class:
    name: str
    attrs: List[Field]


class CodeGenerator:
    def __init__(self, name: str, py_dict: dict):
        self.name = name
        self.py_dict = py_dict
        self.attributes: List[Field] = []

    @staticmethod
    def singularize(word):
        '''change the world from plural to singular'''
        # general plural rules
        rules = [
            ['(?i)(quiz)zes$', '\\1'],
            ['(?i)(matr)ices$', '\\1ix'],
            ['(?i)(vert|ind)ices$', '\\1ex'],
            ['(?i)^(ox)en', '\\1'],
            ['(?i)(alias|status)es$', '\\1'],
            ['(?i)(octop|vir)i$', '\\1us'],
            ['(?i)(cris|ax|test)es$', '\\1is'],
            ['(?i)(shoe)s$', '\\1'],
            ['(?i)(o)es$', '\\1'],
            ['(?i)(bus)es$', '\\1'],
            ['(?i)([m|l])ice$', '\\1ouse'],
            ['(?i)(x|ch|ss|sh)es$', '\\1'],
            ['(?i)(m)ovies$', '\\1ovie'],
            ['(?i)(s)eries$', '\\1eries'],
            ['(?i)([^aeiouy]|qu)ies$', '\\1y'],
            ['(?i)([lr])ves$', '\\1f'],
            ['(?i)(tive)s$', '\\1'],
            ['(?i)(hive)s$', '\\1'],
            ['(?i)([^f])ves$', '\\1fe'],
            ['(?i)(^analy)ses$', '\\1sis'],
            ['(?i)((a)naly|(b)a|(d)iagno|(p)arenthe|(p)rogno|(s)ynop|(t)he)ses$', '\\1\\2sis'],
            ['(?i)([ti])a$', '\\1um'],
            ['(?i)(n)ews$', '\\1ews'],
            ['(?i)s$', '']
        ]

        # irregular word plural rules and special cases
        special_rules = {
            'aircraft': 'aircraft',
            'children': 'child',
            'deer': 'deer',
            'fish': 'fish',
            'feet': 'foot',
            'geese': 'goose',
            'men': 'man',
            'women': 'woman',
            'people': 'person',
            'sheep': 'sheep',
            'species': 'species',
            'teeth': 'tooth',
        }

        # handling irregular plural rules and special cases
        if word in special_rules:
            return special_rules[word]

        # handles general plural rules
        for rule in rules:
            pattern, replace = rule
            if re.search(pattern, word):
                return re.sub(pattern, replace, word)

        return word

    def gen_cls_name(self, name: Optional[str]) -> str:
        if not name:
            random_name = ''
            return f"Class{random_name}"
        else:
            cleaned = ''.join(re.findall(r'([A-Za-z])', name.title()))
            return self.singularize(cleaned)

    def parse_dict(self, attr_dict: dict[str, Any]):
        sub_dicts = []
        for name, value in sorted(attr_dict.items()):
            if isinstance(value, bool):
                field = Field(name, Type.boolean)
                self.attributes.append(field)

            elif isinstance(value, int):
                field = Field(name, Type.integer)
                self.attributes.append(field)

            elif isinstance(value, float):
                field = Field(name, Type.decimal)
                self.attributes.append(field)

            elif isinstance(value, str):
                field = Field(name, Type.string)
                self.attributes.append(field)

            elif isinstance(value, list):
                pass

            elif isinstance(value, dict):
                sub_name = self.gen_cls_name(name)
                sub_attrs = self.parse_dict(value)
                sub_dicts.append((sub_name, sub_attrs))

            else:
                pass

    def dict_to_class(self):
        pass

    def generage(self) -> str:
        raise NotImplementedError


class PythonGenerator(CodeGenerator):
    HEAD = ('@dataclass\n'
            'def %(name)s:\n')

    def generage(self):
        head = self.HEAD % {'name': self.name}
        body = '\n'.join([f'    {f.name}: {f.ftype}' for f in self.attributes])
        return head + body
