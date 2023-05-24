# JSON Formator

[![Build Status](https://github.com/seamile/jsonfmt/actions/workflows/python-package.yml/badge.svg)](https://github.com/seamile/jsonfmt/actions)
[![PyPI Version](https://img.shields.io/pypi/v/jsonfmt?color=blue&label=Version&logo=python&logoColor=white)](https://pypi.org/project/jsonfmt/)
[![Installs](https://static.pepy.tech/personalized-badge/jsonfmt?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Installs)](https://pepy.tech/project/jsonfmt)
[![Code Grade](https://app.codacy.com/project/badge/Grade/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Test Coverage](https://app.codacy.com/project/badge/Coverage/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

**jsonfmt** is a CLI tool for pretty printing or compressing JSON objects.

It has the following features:

- [Print JSON with **hightlight** and **pretty format** from files or stdin.](#1-pretty-print-json-object)
- [Minimize JSON to a single line.](#2-minimize-the-json-object)
- [Output part of a large JSON via jsonpath.](#3-use-jsonpath-to-match-part-of-the-object)
- [Format JSON to TOML or YAML](#4-format-json-to-toml-or-yaml)
- [Convert between other formats](#5-convert-between-json-toml-and-yaml-formats)


## Install

```shell
$ pip install jsonfmt
```


## Usage

```shell
$ jsonfmt [Options] [Files ...]
```

- Positional arguments:

    - `files`: the files that will be processed

- Options:
  - `-h, --help`: show this help message and exit
  - `-c`: compact the json object to a single line
  - `-e`: escape non-ASCII characters
  - `-f {json,toml,yaml}`: the format to output (default: json)
  - `-i INDENT`: number of spaces to use for indentation (default: 2)
  - `-O`: overwrite the formated text to original file
  - `-p JSONPATH`: output part of the object via jsonpath
  - `-v`: show the version


## Example

There are some test data in folder `test`:
```
test/
|- example.json
|- example.toml
|- example.yaml
```

### 1. Pretty print JSON object.

- read from file

    ```shell
    $ jsonfmt test/example.json
    ```

    Output:
    ```json
    {
        "actions": [
            {
            "calorie": 294.9,
            "date": "2021-03-02",
            "name": "eat"
            },
            {
            "calorie": -375,
            "date": "2023-04-27",
            "name": "sport"
            }
        ],
        "age": 23,
        "gender": "纯爷们",
        "money": 3.1415926,
        "name": "Bob"
    }
    ```

- read from stdin

    ```shell
    $ cat test/example.json | jsonfmt
    ```

    Output: Ditto.

### 2. Minimize the JSON object.

```shell
$ echo '{ "name": "alex", "age": 21, "items": ["pen", "phone"] }' | jsonfmt -c
```

Output:
```json
{"age":21,"items":["pen","phone"],"name":"alex"}
```

### 3. Use jsonpath to match part of the object.

**jsonfmt** uses a simplified jsonpath syntax.

- It matches JSON objects starting from the root node.

- You can use keys to match dictionaries and indexes to match lists, and use `/` to separate different levels.

    ```shell
    $ jsonfmt -p 'actions/0' test/example.json
    ```

    Output:
    ```json
    {
        "calorie": 294.9,
        "date": "2021-03-02",
        "name": "eat"
    }
    ```

- If you want to match all items in a list, just use `*` to match.

    ```shell
    $ jsonfmt -p 'actions/*/name' test/example.json
    ```

    Output:
    ```json
    [
        "eat",
        "sport"
    ]
    ```

### 4. Format JSON to TOML or YAML.

```shell
$ jsonfmt -f toml test/example.json
```

Output:
```toml
age = 23
gender = "纯爷们"
money = 3.1415926
name = "Bob"
[[actions]]
calorie = 294.9
date = "2021-03-02"
name = "eat"

[[actions]]
calorie = -375
date = "2023-04-27"
name = "sport"
```

### 5. Convert between JSON, TOML and YAML formats.

```shell
# json to yaml
$ jsonfmt -f yaml test/example.json

# yaml to toml
$ jsonfmt -f toml test/example.yaml

# toml to json
$ jsonfmt -f json test/example.toml
```

### 6. Other usages

- use the `-O` parameter to overwrite the file with the result.

```shell
$ jsonfmt -O test/example.json
```

- write the result to a new file (use symbol `>`).

```shell
$ jsonfmt test/example.json > formatted.json
```
