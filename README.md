# JSON Formator

[![Build Status](https://github.com/seamile/jsonfmt/actions/workflows/python-package.yml/badge.svg)](https://github.com/seamile/jsonfmt/actions)
[![PyPI Version](https://img.shields.io/pypi/v/jsonfmt?color=blue&label=Version&logo=python&logoColor=white)](https://pypi.org/project/jsonfmt/)
[![Installs](https://static.pepy.tech/personalized-badge/jsonfmt?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Installs)](https://pepy.tech/project/jsonfmt)
[![Code Grade](https://app.codacy.com/project/badge/Grade/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Test Coverage](https://app.codacy.com/project/badge/Coverage/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

**jsonfmt** is a CLI tool for pretty printing, querying and format conversion JSON documents.

## Features

1. [Print JSON with **hightlight** and **pretty format**.](#1-pretty-print-json-object)
2. [Minimize JSON to a single line.](#2-minimize-the-json-object)
3. [Pick out parts from a large JSON via jsonpath.](#3-pick-out-parts-of-a-large-json-via-jsonpath)
4. [Format JSON to TOML or YAML.](#4-format-json-as-toml-or-yaml)
5. [Conversion between these three formats.](#5-conversion-between-json-toml-and-yaml-formats)
6. [Copy the result to clipboard.](#6-copy-the-result-to-clipboard)


## Install

```shell
$ pip install jsonfmt
```


## Usage

```shell
$ jsonfmt [options] [files ...]
```

- Positional arguments:

    - `files`: the files that will be processed

- Options:

    - `-h, --help`: show this help message and exit
    - `-c`: compact the json object to a single line
    - `-C`: copy the result to clipboard
    - `-e`: escape non-ASCII characters
    - `-f {json,toml,yaml}`: the format to output (default: json)
    - `-i INDENT`: number of spaces for indentation (default: 2)
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
    # format the json with 4-space indentaion
    $ jsonfmt -i 4 test/example.json
    ```

    *Output:*

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
    $ cat test/example.json | jsonfmt -i 4
    ```

    *Output*: Ditto.

### 2. Minimize the JSON object.

```shell
$ echo '{
    "name": "alex",
    "age": 21,
    "items": [
        "pen",
        "phone"
    ]
}' | jsonfmt -c
```

*Output:*

```json
{"age":21,"items":["pen","phone"],"name":"alex"}
```

### 3. Pick out parts of a large JSON via JSONPath.

**JSONPath** is a way to query the sub-elements of a JSON document.

It likes the XPath for xml, which can extract part of the content of a given JSON document through a simple syntax.

JSONPath syntax reference <https://goessner.net/articles/JsonPath/> and <https://datatracker.ietf.org/doc/id/draft-goessner-dispatch-jsonpath-00.html>

Some examples:

- pick out the first actions in `example.json`

    ```shell
    $ jsonfmt -p '$.actions[0]' test/example.json
    ```

    *Output:*

    ```json
    [
        {
            "calorie": 294.9,
            "date": "2021-03-02",
            "name": "eat"
        }
    ]
    ```

- Filters all occurrences of the `name` field in the JSON.

    ```shell
    $ jsonfmt -p '$..name' test/example.json
    ```

    *Output:*

    ```json
    [
        "Bob",
        "eat",
        "sport"
    ]
    ```

### 4. Format JSON as TOML or YAML.

```shell
$ jsonfmt test/example.json -f toml
```

*Output:*

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

### 5. Conversion between JSON, TOML and YAML formats.

<div style="color: orange"><strong>Note this:</strong></div>
The `null` value is invalid in TOML. Therefore, any null values in JSON or YAML will be removed when converting to TOML.

```shell
# json to yaml
$ jsonfmt test/example.json -f yaml

# yaml to toml
$ jsonfmt test/example.yaml -f toml

# toml to json
$ jsonfmt test/example.toml -f json
```

### 6. Copy the result to clipboard.

```shell
$ jsonfmt -C test/example.json

# Output
jsonfmt: result copied to clipboard.
```

Once you've done the above, you can then use <kbd>ctrl</kbd>+<kbd>v</kbd> or <kbd>cmd</kbd>+<kbd>v</kbd> to paste the result anywhere on your computer.

<div style="color: orange"><strong>Note these:</strong></div>

- When you specify the `-C` option, any output destination other than the clipboard will be ignored.
- When you process multiple files, only the last result will be preserved in the clipboard.

### 7. Output to file.

- use the `-O` parameter to overwrite the file with the result.

```shell
$ jsonfmt -O test/example.json
```

- write the result to a new file (use symbol `>`).

```shell
$ jsonfmt test/example.json > formatted.json
```
