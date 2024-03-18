<div align="center">
  <img src="logo.svg" width="150">
  <h1>JSON Formatter</h1>
</div>

<div align="center">

[![Build Status](https://github.com/seamile/jsonfmt/actions/workflows/python-package.yml/badge.svg)](https://github.com/seamile/jsonfmt/actions)
[![PyPI Version](https://img.shields.io/pypi/v/jsonfmt?color=blue&label=Version&logo=python&logoColor=white)](https://pypi.org/project/jsonfmt/)
[![Installs](https://static.pepy.tech/personalized-badge/jsonfmt?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Installs)](https://pepy.tech/project/jsonfmt)
[![Code Grade](https://app.codacy.com/project/badge/Grade/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Test Coverage](https://app.codacy.com/project/badge/Coverage/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

</div>

**jsonfmt** is a super awesome JSON tool. It's just as powerful as [jq](https://github.com/jqlang/jq), but easier to use.

You can use it for pretty-printing, querying and conversion JSON data.
It is used for pretty-printing, querying and conversion JSON data.

## Features

- [1. Pretty print JSON data.](#1-pretty-print-json-data)
    - [Syntax hight and indenation.](#syntax-hight-and-indenation)
    - [Read JSON from pipeline.](#read-json-from-pipeline)
- [2. Features for handling large JSON data.](#2-features-for-handling-large-json-data)
    - [View a large JSON with pager-mode.](#view-a-large-json-with-pager-mode)
    - [Show the overview of a large JSON.](#show-the-overview-of-a-large-json)
    - [Copy the result to clipboard.](#copy-the-result-to-clipboard)
- [3. Minimize the JSON data.](#3-minimize-the-json-data)
- [4. Extract a portion of a large JSON via JMESPath or JSONPath.](#4-extract-a-portion-of-a-large-json-via-jmespath-or-jsonpath)
    - [JMESPath examples](#jmespath-examples)
    - [JSONPath examples](#jsonpath-examples)
    - [Query for TOML and YAML](#query-for-toml-and-yaml)
- [5. Convert formats between JSON, TOML and YAML.](#5-convert-formats-between-json-toml-and-yaml)
    - [JSON to TOML and YAML](#json-to-toml-and-yaml)
    - [TOML to JSON and YAML](#toml-to-json-and-yaml)
    - [YAML to JSON and TOML](#yaml-to-json-and-toml)
- [6. Modify some values in the input data.](#6-modify-some-values-in-the-input-data)
    - [Add items](#add-items)
    - [Modify items](#modify-items)
    - [Pop items](#pop-items)
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
    - `-f {json,toml,yaml}`: the format to output (default: same as input)
    - `-i {0-8,t}`: number of spaces for indentation (default: 2)
    - `-o`: show data structure overview
    - `-O`: overwrite the formated text to original file
    - `-l {jmespath,jsonpath}`: the language for querying (default: jmespath)
    - `-p QUERYPATH`: the path for querying
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

### 1. Pretty print JSON data.

#### Syntax hight and indenation.

In the Python, there is a built-in tool for format JSON data: `python -m json.tool`.
But its feature is too simple. So *jsonfmt* extends its capabilities, such as *highlight*, *pager*, *overview*, etc.

By default, indentation is 2 spaces. You can specify it with option `-i`.
The number of spaces allowed is between 0 and 8. Set it to `t` if you want to use <kbd>tab</kbd> for indentation.

The `-s` option is used to sort the output of dictionaries alphabetically by key.

If there are some non-ASCII characters in the JSON data, you can use `-e` to eascape them.

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

### 2. Features for handling large JSON data.

#### View a large JSON with pager-mode.

The pager-mode is similar to the command `more`.

*jsonfmt* will automatically present the result in pager-mode when the JSON data is too large to overflow the window display area.

The key-binding of the pager-mode is same as command `more`:

| key                          | description               |
|------------------------------|---------------------------|
| <kbd>j</kbd>                 | forward  by line          |
| <kbd>k</kbd>                 | backward by line          |
| <kbd>f</kbd>                 | forward by page           |
| <kbd>ctrl</kbd>+<kbd>f</kbd> | forward by page           |
| <kbd>b</kbd>                 | backward by page          |
| <kbd>ctrl</kbd>+<kbd>b</kbd> | backward by page          |
| <kbd>g</kbd>                 | go to the top of the page |
| <kbd>G</kbd>                 | go to the bottom          |
| <kbd>/</kbd>                 | search mode               |
| <kbd>q</kbd>                 | quit pager-mode           |

There is a big JSON from GitHub, you can paste this command into terminal to try the pager-mode:

```shell
curl -s 'https://api.github.com/repos/seamile/jsonfmt/commits?per_page=10' | jsonfmt
```

#### Show the overview of a large JSON.

Sometimes we just want to see the overview and don't care about the details of the JSON data. In this case the `-o` option can be used.

It will clear sublist of the JSON and modify strings to '...' in the overview.

If the *root* node of the JSON data is a list, only the first child element will be reserved in the overview.

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


### 3. Minimize the JSON data.

The `-c` option used to suppress all whitespace and newlines to compact the JSON data into a single line.

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

### 4. Extract a portion of a large JSON via JMESPath or JSONPath.

Unlike from jq's private solution, `jsonfmt` uses both [JMESPath](https://jmespath.org/) and [JSONPath](https://datatracker.ietf.org/doc/id/draft-goessner-dispatch-jsonpath-00.html) as its query language.

Among the many JSON query languages, `JMESPath` is the most popular one ([compared here](https://npmtrends.com/JSONPath-vs-jmespath-vs-jq-vs-json-path-vs-json-query-vs-jsonata-vs-jsonpath-vs-jsonpath-plus-vs-node-jq)). It is more general than `jq`, and more intuitive and powerful than `JSONPath`. So I prefer to use it.

Like the XPath for xml, `JMESPath` can elegantly extract parts of a given JSON data with simple syntax. The official tutorial of JMESPath is [here](https://jmespath.org/tutorial.html).

#### JMESPath examples

- pick out the first actions in `example.json`

    ```shell
    $ jsonfmt -p 'actions[0]' test/example.json
    ```

    *Output:*

    ```json
    {
        "calorie": 294.9,
        "date": "2021-03-02",
        "name": "eat"
    }
    ```

- Filter all items in `actions` with `calorie` > 0.

    ```shell
    $ jsonfmt -p 'actions[?calorie>`0`]' test/example.json
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

- Show all the keys and actions' length.

    ```shell
    $ jsonfmt -p '{all_keys:keys(@), actions_len:length(actions)}' test/example.json
    ```

    *Output:*

    ```json
    {
        "all_keys": [
            "actions",
            "age",
            "gender",
            "money",
            "name"
    ],
        "actions_len": 2
    }
    ```

- Sort `actions` by `calorie` and redefine a dict.

    ```shell
    $ jsonfmt -p 'sort_by(actions, &calorie)[].{name: name, calorie:calorie}' test/example.json
    ```

    *Output:*

    ```json
    [
        {
            "name": "sport",
            "calorie": -375
        },
        {
            "name": "eat",
            "calorie": 294.9
        }
    ]
    ```

[More examples of JMESPath](https://jmespath.org/examples.html).

#### JSONPath examples

The syntax of `JSONPath` is very similar to that of `JMESPath`. Everything that `JSONPath` can do `JMESPath` can also do, except using relative path querying. So `JSONPath` can be used as a supplementary query method of `JMESPath`.

- Filter all `name` fields by relative path:

    ```shell
    # use `-l` to specify the query language of JSON
    $ jsonfmt.py -l jsonpath -p '$..name' test/example.json
    ```

    *Output:*

    ```json
    [
        "Bob",
        "eat",
        "sport"
    ]
    ```

#### Query for TOML and YAML

**Amazingly**, you can do all of the above with TOML and YAML in the same way, and convert the result format arbitrarily. It is even possible to process all three formats simultaneously in a single command.

- Read the data from toml file, and convert the result to yaml

    ```shell
    $ jsonfmt -p '{all_keys:keys(@), actions_len:length(actions)}' test/example.toml -f yaml
    ```

    *Output:*

    ```yaml
    all_keys:
    - age
    - gender
    - money
    - name
    - actions
    actions_len: 2
    ```

- Handle three formats simultaneously

    ```shell
    $ jsonfmt.py -p 'actions[0]' test/example.json test/example.toml test/example.yaml
    ```

    *Output:*

    ```
    {
        "calorie": 294.9,
        "date": "2021-03-02",
        "name": "eat"
    }

    calorie = 294.9
    date = "2021-03-02"
    name = "eat"

    calorie: 294.9
    date: '2021-03-02'
    name: eat
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

The format is `--set 'key=value'`. When you need to modify multiple values ​​you can use `;` to separate: `--set 'k1=v1;k2=v2'`. If the key-value pair dose not exist, it will be added.

For the items in list, use `key[i]` or `key.i` to specify. If the index is greater than or equal to the number of elements, the value will be appended.

#### Add items

```shell
# add `country` key and append one item for `actions`
$ jsonfmt --set 'country=China; actions[2]={"name": "drink"}' test/example.json
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
        },
        {
            "name": "drink"
        }
    ],
    "age": 23,
    "country": "China",
    "gender": "纯爷们",
    "money": 3.1415926,
    "name": "Bob"
}
```

#### Modify items

```shell
# modify money and actions[1]["name"]
$ jsonfmt --set 'money=1000; actions[1].name=swim' test/example.json
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
            "name": "swim"
        }
    ],
    "age": 23,
    "gender": "纯爷们",
    "money": 1000,
    "name": "Bob"
}
```

#### Pop items

```shell
# pop `gender` and actions[1]
$ jsonfmt --pop 'gender; actions[1]' test/example.json
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
jsonfmt --set 'skills=["Django","Flask"];money=1000' --pop 'gender;actions[1]' test/example.json
```

**Note**, however, that the above command will not modify the original JSON file.
If you want to do this, read below please.

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


## TODO

[ ] add feature: json diff
    - args: `-d`, `--diff`
    - tools: `code --diff`, `vimdiff`, `diff`
[ ] add feature: xml format
[ ] add alias cmd: jf
[ ] 增加文档的中文版
