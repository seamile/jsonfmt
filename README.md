# JSON Formator

[![Build Status](https://github.com/seamile/jsonfmt/actions/workflows/python-package.yml/badge.svg)](https://github.com/seamile/jsonfmt/actions)
[![PyPI Version](https://img.shields.io/pypi/v/jsonfmt?color=blue&label=Version&logo=python&logoColor=white)](https://pypi.org/project/jsonfmt/)
[![Installs](https://static.pepy.tech/personalized-badge/jsonfmt?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Installs)](https://pepy.tech/project/jsonfmt)
[![Code Grade](https://app.codacy.com/project/badge/Grade/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Test Coverage](https://app.codacy.com/project/badge/Coverage/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

**jsonfmt** is a powerful tool for handling JSON document.

It is similar to [jq](https://github.com/jqlang/jq), but simpler.

## Features

- [1. Pretty print JSON document.](#1-pretty-print-json-document)
    - [Syntax hight and indenation.](#syntax-hight-and-indenation)
    - [Read JSON from pipeline.](#read-json-from-pipeline)
- [2. Features for handling large JSON document.](#2-features-for-handling-large-json-document)
    - [View a large JSON with pager-mode.](#view-a-large-json-with-pager-mode)
    - [Show the overview of a large JSON.](#show-the-overview-of-a-large-json)
    - [Copy the result to clipboard.](#copy-the-result-to-clipboard)
- [3. Minimize the JSON document.](#3-minimize-the-json-document)
- [4. Pick out parts of a large JSON via JSONPath.](#4-pick-out-parts-of-a-large-json-via-jsonpath)
- [5. Convert formats between JSON, TOML and YAML.](#5-convert-formats-between-json-toml-and-yaml)
    - [JSON to TOML and YAML](#json-to-toml-and-yaml)
    - [TOML to JSON and YAML](#toml-to-json-and-yaml)
    - [YAML to JSON and TOML](#yaml-to-json-and-toml)
- [6. Modify some values in the input data.](#6-modify-some-values-in-the-input-data)
    - [Add and modify some items.](#add-and-modify-some-items)
    - [Pop some items.](#pop-some-items)
- [7. Output to file.](#7-output-to-file)


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
    - `-c`: suppress all whitespace separation
    - `-C`: copy the result to clipboard
    - `-e`: escape non-ASCII characters
    - `-f {json,toml,yaml}`: the format to output (default: None)
    - `-i {0-8,t}`: number of spaces for indentation (default: 2)
    - `-o`: show data structure overview
    - `-O`: overwrite the formated text to original file
    - `-p JSONPATH`: output part of the object via jsonpath
    - `-s`: sort keys of objects on output
    - `--set 'foo.k1=v1;k2[i]=v2'`: set the keys to values (seperated by `;`)
    - `--pop 'k1;foo.k2;k3[i]'`: pop the specified keys (seperated by `;`)
    - `-v`: show the version


## Example

There are some test data in folder `test`:

```
test/
|- example.json
|- example.toml
|- example.yaml
```

### 1. Pretty print JSON document.

#### Syntax hight and indenation.

In the Python, there is a built-in tool for format JSON document: `python -m json.tool`.
But its feature is too simple. So *jsonfmt* extends its capabilities, such as *highlight*, *pager*, *overview*, etc.

By default, indentation is 2 spaces. You can specify it with option `-i`.
The number of spaces allowed is between 0 and 8. Set it to `t` if you want to use <kbd>tab</kbd> for indentation.

The `-s` option is used to sort the output of dictionaries alphabetically by key.

If there are some non-ASCII characters in the JSON document, you can use `-e` to eascape them.

```shell
$ jsonfmt -s -i 4 test/example.json
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

#### Read JSON from pipeline.

Sometimes the JSON you want to process comes from other commands. Just use `|` to read it from pipeline.

```shell
$ cat test/example.json | jsonfmt -i 4
```

### 2. Features for handling large JSON document.

#### View a large JSON with pager-mode.

The pager-mode is similar to the command `more`.

*jsonfmt* will automatically present the result in pager-mode when the JSON document is too large to overflow the window display area.

The key-binding of the pager-mode is same as command `more`:

- <kbd>j</kbd> / <kbd>k</kbd> to forward / backward by line.
- <kbd>f</kbd> or <kbd>ctrl</kbd>+<kbd>f</kbd> to forward by page.
- <kbd>b</kbd> or <kbd>ctrl</kbd>+<kbd>b</kbd> to backward by page.
- <kbd>g</kbd> to go to the top of the page, and <kbd>G</kbd> to the bottom.
- <kbd>q</kbd> to exit.

There is a big JSON from GitHub, you can paste this command into terminal to try the pager-mode:

```shell
curl -s 'https://api.github.com/repos/seamile/jsonfmt/commits?per_page=10' | jsonfmt
```

#### Show the overview of a large JSON.

Sometimes we just want to see the overview and don't care about the details of the JSON document. In this case the `-o` option can be used.

It will clear sublist of the JSON and modify strings to '...' in the overview.

If the *root* node of the JSON document is a list, only the first child element will be reserved in the overview.

```shell
$ jsonfmt -o test/test.json
```

*Output:*

```json
{
    "actions": [],
    "age": 23,
    "gender": "...",
    "money": 3.1415926,
    "name": "..."
}
```

#### Copy the result to clipboard.

If you want to copy the result into a file and the output of JSON is more than one page in the terminal, it's going to be hard to do.

At this time, you can specify the `-C` option to copy the result to the clipboard automatically.

```shell
$ jsonfmt -C test/example.json

# Output
jsonfmt: result copied to clipboard.
```

Once you've done the above, you can then use <kbd>ctrl</kbd>+<kbd>v</kbd> or <kbd>cmd</kbd>+<kbd>v</kbd> to paste the result anywhere on your computer.

<div style="color: orange"><strong>Note these:</strong></div>

- When you specify the `-C` option, any output destination other than the clipboard will be ignored.
- When you process multiple files, only the last result will be preserved in the clipboard.


### 3. Minimize the JSON document.

The `-c` option used to suppress all whitespace and newlines to compact the JSON document into a single line.

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

### 4. Pick out parts of a large JSON via JSONPath.

**JSONPath** is a way to query the sub-elements of a JSON document.

It likes the XPath for xml, which can extract part of the content of a given JSON document through a simple syntax.

JSONPath syntax reference: [goessner.net](https://goessner.net/articles/JsonPath/), [ietf.org](https://datatracker.ietf.org/doc/id/draft-goessner-dispatch-jsonpath-00.html).

Some examples:

- pick out the first actions in `example.json`

    ```shell
    $ jsonfmt -p 'actions[0]' test/example.json
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

### 5. Convert formats between JSON, TOML and YAML.

The *jsonfmt* can recognize any format of JSON, TOML and YAML from files or `stdin`. Either formats can be converted to the other by specifying the "-f" option.

<div style="color: orange"><strong>Note that:</strong></div>
The `null` value is invalid in TOML. Therefore, any null values from JSON or YAML will be removed when converting to TOML.

#### JSON to TOML and YAML

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

```shell
$ jsonfmt test/example.json -f yaml
```

*Output:*

```yaml
actions:
- calorie: 294.9
  date: '2021-03-02'
  name: eat
- calorie: -375
  date: '2023-04-27'
  name: sport
age: 23
gender: 纯爷们
money: 3.1415926
name: Bob
```

#### TOML to JSON and YAML

```shell
# toml to json
$ jsonfmt test/example.toml -f json
# toml to yaml
$ jsonfmt test/example.toml -f yaml
```

#### YAML to JSON and TOML

```shell
# yaml to json
$ jsonfmt test/example.yaml -f json

# yaml to toml
$ jsonfmt test/example.yaml -f toml
```

### 6. Modify some values in the input data.

Use the `--set` and `--pop` options when you want to change something in the input documents.

The format is `--set 'key1=value1'`. When you need to modify multiple values ​​you can use `;` to separate: `--set 'k1=v1;k2=v2'`. If the key-value pair dose not exist, it will be added.

For the items in list, use `key[i]` or `key.i` to specify. But it doesn't support adding new elements.

#### Add and modify some items.

```shell
# add a key-value pair and modify the money field
$ jsonfmt --set 'skills=["Django","Flask"];money=1000' test/example.json
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
    "money": 1000,
    "name": "Bob",
    "skills": [
        "Django",
        "Flask"
    ]
}
```

#### Pop some items.

```shell
# remove the gender field and action[1]
$ jsonfmt --pop 'gender;action[1]' test/example.json
```

*Output:*

```json
{
    "actions": [
        {
            "calorie": 294.9,
            "date": "2021-03-02",
            "name": "eat"
        }
    ],
    "age": 23,
    "money": 3.1415926,
    "name": "Bob"
}
```

Of course you can use `--set` and `--pop` together.

```shell
jsonfmt --set 'skills=["Django","Flask"];money=1000' --pop 'gender;action[1]' test/example.json
```

**Note**, however, that the above command will not modify the original JSON file.
If you want to do this, then please read below.

### 7. Output to file.

- use the `-O` parameter to overwrite the file with the result.

    This option will be forced to close when `-o` is specified

    ```shell
    $ jsonfmt --set 'name=Alex' -O test/example.json
    ```

- write the result to a new file (use symbol `>`).

    ```shell
    $ jsonfmt test/example.json > formatted.json
    ```
