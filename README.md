<div align="center">
  <img src="logo.svg" width="150">
  <h1>𝑱𝒔𝒐𝒏𝑭𝒎𝒕</h1>
</div>


<div align="center">

[![Build Status](https://github.com/seamile/jsonfmt/actions/workflows/python-package.yml/badge.svg)](https://github.com/seamile/jsonfmt/actions)
[![PyPI Version](https://img.shields.io/pypi/v/jsonfmt?color=blue&label=Version&logo=python&logoColor=white)](https://pypi.org/project/jsonfmt/)
[![Installs](https://static.pepy.tech/personalized-badge/jsonfmt?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Installs)](https://pepy.tech/project/jsonfmt)
[![Code Grade](https://app.codacy.com/project/badge/Grade/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Test Coverage](https://app.codacy.com/project/badge/Coverage/1e12e3cd8c8342bca68db4caf5b6a31d)](https://app.codacy.com/gh/seamile/jsonfmt/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

<a href="README_CN.md">🇨🇳 中文版</a>　<a style="color: grey;">🇬🇧 English</a>
</div>

**_jsonfmt_** (JSON Formatter) is a simple yet powerful JSON processing tool.

As we all know, Python has a built-in tool for formatting JSON data: `python -m json.tool`. However, its functionality is too simple, so **jsonfmt** extends it with many practical features:

🎨 It can not only print JSON data in a pretty way,

🔄 But also convert JSON, TOML, XML and YAML data formats to each other,

🔎 And even extract content from JSON data using JMESPATH or JSONPATH.

🧐 You can even use **jsonfmt** to compare differences between two JSON or other formatted data.


- [Quick Start](#quick-start)
    - [Installation](#installation)
    - [Usage](#usage)
- [User Guide](#user-guide)
    - [1. Pretty Print JSON Data](#1-pretty-print-json-data)
    - [2. Minimize the JSON data](#2-minimize-the-json-data)
    - [3. Extract Partial Content from JSON Data](#3-extract-partial-content-from-json-data)
    - [4. Format Conversion](#4-format-conversion)
    - [5. Diff Comparison](#5-diff-comparison)
    - [6. Handle Large JSON Data Conveniently](#6-handle-large-json-data-conveniently)
    - [7. Modify Values in Input Data](#7-modify-values-in-input-data)
    - [8. Output to File](#8-output-to-file)
- [TODO](#todo)


## Quick Start

### Installation

```shell
$ pip install jsonfmt
```

### Usage

1. Process data from files.

  ```shell
  $ jf [options] [data_files ...]
  ```

2. Process data from `stdin`.

  ```shell
  $ echo '{"hello": "world"}' | jf [options]
  ```

**Positional Arguments**

`files`: The data files to process, supporting JSON / TOML / XML / YAML formats.

**Options**

- `-h`: Show this help documentation and exit.
- `-C`: CopyMode, which will copy the processing result to the clipboard.
- `-d`: DiffMode, which compares the difference between the two input data.
- `-D DIFFTOOL`: DifftoolMode, similar to "DiffMode". You can specify a tool to perform diff comparisons.
- `-o`: OverviewMode, which can display an overview of the structure of the data, helping to quickly understand larger data.
- `-O`: OverwriteMode, which will overwrite the original file with the formated text.
- `-c`: Suppress all whitespace separation (most compact), only valid for JSON.
- `-e`: Escape all characters to ASCII codes.
- `-f`: The format to output (default: same as input data format, options: `json` / `toml` / `xml` / `yaml`).
- `-i`: Number of spaces for indentation (default: 2, range: 0~8, set to 't' to use <kbd>Tab</kbd> as indentation).
- `-l`: Query language for extracting data (default: auto-detect, options: jmespath / jsonpath).
- `-p QUERYPATH`: JMESPath or JSONPath query path.
- `-s`: Sort the output of dictionaries alphabetically by key.
- `--set 'foo.k1=v1;k2[i]=v2'`: Key-value pairs to add or modify (separated by ";").
- `--pop 'k1;foo.k2;k3[i]'`: Key-value pairs to delete (separated by ";").
- `-v`: Show the version.


## User Guide

In order to demonstrate the features of jsonfmt, we need to first create a test data and save it to the file example.json. The file contents are as follows:

```json
{
    "name": "Bob",
    "age": 23,
    "gender": "纯爷们",
    "money": 3.1415926,
    "actions": [
        {
            "name": "eating",
            "calorie": 1294.9,
            "date": "2021-03-02"
        },
        {
            "name": "sporting",
            "calorie": -2375,
            "date": "2023-04-27"
        },
        {
            "name": "sleeping",
            "calorie": -420.5,
            "date": "2023-05-15"
        }
    ]
}
```

Then, convert this data to TOML, XML and YAML formats, and save them as example.toml, example.xml and example.yaml respectively.

These data files can be found in the *test* folder of the source code:

```
test/
|- example.json
|- example.toml
|- example.xml
|- example.yaml
```

### 1. Pretty Print JSON Data

#### Syntax Highlighting and Indentation

The default working mode of jsonfmt is to format the data and print it with syntax highlighting.

The option `-i` specifies the number of spaces for indentation. By default, it is 2 spaces, and the number of spaces allowed is between 0 and 8. If you want to use the <kbd>tab</kbd> as indentation, set it to `t`.

The `-s` option is used to sort the dictionary alphabetically by key.

If there are some non-ASCII characters in the JSON data, you can use `-e` to escape them.

```shell
$ jf -s -i 4 test/example.json
```

Output:

```json
{
    "actions": [
        {
            "calorie": 1294.9,
            "date": "2021-03-02",
            "name": "eating"
        },
        {
            "calorie": -2375,
            "date": "2023-04-27",
            "name": "sporting"
        },
        {
            "calorie": -420.5,
            "date": "2023-05-15",
            "name": "sleeping"
        }
    ],
    "age": 23,
    "gender": "纯爷们",
    "money": 3.1415926,
    "name": "Bob"
}
```

#### Read JSON from Pipeline

Sometimes the data to be processed comes from the output of other commands. Just use the pipe character `|` to connect the two commands and then take it from the `stdin`.

```shell
$ curl -s https://jsonplaceholder.typicode.com/posts/1 | jf -i 4
```

Output:

```json
{
    "userId": 1,
    "id": 1,
    "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
    "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nrep..."
}

```

### 2. Minimize the JSON data

The `-c` option used to suppress all whitespace and newlines to compact the JSON data into a single line.

```shell
$ echo '{
    "name": "alex",
    "age": 21,
    "items": [
        "pen",
        "phone"
    ]
}' | jf -c
```

Output:

```json
{"name":"alex","age":21,"items":["pen","phone"]}
```

### 3. Extract Partial Content from JSON Data

jsonfmt uses both [**JMESPath**](https://jmespath.org/) and [**JSONPath**](https://datatracker.ietf.org/doc/id/draft-goessner-dispatch-jsonpath-00.html) as its query languages.

**JMESPath** (JSON Meta Language for Expression Path) is a query language introduced by AWS for processing JSON data. Among the many JSON query languages, JMESPath seems to be the most widely-used, fastest-growing, and highest-rated. Its syntax is more concise and more universal than [**jq**](https://jqlang.github.io/jq/), and its functionality is more powerful and feature-rich than JSONPath. Therefore, I prefer to use it as the primary JSON query language.

JMESPath can elegantly use simple syntax to extract part of the content from JSON data, and also compose the filtered data into a new object or array. The official JMESPath tutorial is [here](https://jmespath.org/tutorial.html).

#### JMESPath Examples

- Extract the first item of `actions` from *example.json*:

    ```shell
    $ jf -p 'actions[0]' test/example.json
    ```

    Output:

    ```json
    {
        "name": "eating",
        "calorie": 1294.9,
        "date": "2021-03-02"
    }
    ```

- Filter all items with `calorie < 0` from `actions`.

    ```shell
    # Here, `0` means 0 is a number
    $ jf -p 'actions[?calorie<`0`]' test/example.json
    ```

    Output:

    ```json
    [
        {
            "name": "sporting",
            "calorie": -2375,
            "date": "2023-04-27"
        },
        {
            "name": "sleeping",
            "calorie": -420.5,
            "date": "2023-05-15"
        }
    ]
    ```

- Show all keys and the length of `actions`.

    ```shell
    $ jf -p '{all_keys:keys(@), actions_len:length(actions)}' test/example.json
    ```

    Output:

    ```json
    {
        "all_keys": [
            "name",
            "age",
            "gender",
            "money",
            "actions"
        ],
        "actions_len": 3
    }
    ```

- Sort the items in `actions` by their `calorie` value, and define the result as a new dictionary.

    ```shell
    $ jf -p 'sort_by(actions, &calorie)[].{foo: name, bar:calorie}' test/example.json
    ```

    Output:

    ```json
    [
        {
            "foo": "sporting",
            "bar": -2375
        },
        {
            "foo": "sleeping",
            "bar": -420.5
        },
        {
            "foo": "eating",
            "bar": 1294.9
        }
    ]
    ```

[More JMESPath examples](https://jmespath.org/examples.html).

#### JSONPath Examples

JSONPath was inspired by the design of XPath. Therefore, it can precisely locate any element in the JSON document through path expressions, similar to XPath, enabling efficient retrieval, filtering, and operation of complex nested data.

Unlike the tag hierarchical structure of XML, JSONPath specially handles JSON key-value pairs and arrays, allowing users to conveniently access multi-level object properties, iterate over objects and arrays, and filter data based on conditions.

Some queries that are difficult to handle with JMESPath can be easily achieved with JSONPath.

- Filter all `name` fields using relative paths:

    ```shell
    # Use -l to specify the query language as JSONPath
    $ jf -l jsonpath -p '$..name' test/example.json
    ```

    Output:

    ```json
    [
        "Bob",
        "eating",
        "sporting",
        "sleeping"
    ]
    ```

#### Querying TOML, XML and YAML

One of the powerful features of jsonfmt is that you can process TOML, XML and YAML in exactly the same way as JSON, and freely convert the result format. You can even process these four formats simultaneously in one command.

- Read data from a toml file and output in YAML format

    ```shell
    $ jf -p '{all_keys:keys(@), actions_len:length(actions)}' test/example.toml -f yaml
    ```

    Output:

    ```yaml
    all_keys:
    - name
    - age
    - gender
    - money
    - actions
    actions_len: 3
    ```

- Process three formats at once

    ```shell
    $ jf -p 'actions[0]' test/example.json test/example.toml test/example.yaml
    ```

    Output:

    ```yaml
    1. test/example.json
    {
        "name": "eating",
        "calorie": 1294.9,
        "date": "2021-03-02"
    }

    2. test/example.toml
    name = "eating"
    calorie = 1294.9
    date = "2021-03-02"

    3. test/example.xml
    <?xml version="1.0" ?>
    <root>
        <name>eating</name>
        <calorie>1294.9</calorie>
        <date>2021-03-02</date>
    </root>

    4. test/example.yaml
    name: eating
    calorie: 1294.9
    date: '2021-03-02'
    ```


### 4. Format Conversion

*jsonfmt* supports processing JSON, TOML, XML and YAML formats. Each format can be converted to other formats by specifying the "-f" option.

<div style="color: orange"><strong>Note:</strong></div>

1. `null` is not supported in TOML. Therefore, all `null` values will be deleted when converting from other formats to TOML.

2. XML does not support multi-dimensional arrays. Therefore, if the original data contains multi-dimensional arrays, a wrong data will be generated during the conversion to XML format.

#### Example 1. JSON to YAML

```shell
$ jf test/example.json -f yaml
```

Output:

```yaml
name: Bob
age: 23
gender: 纯爷们
money: 3.1415926
actions:
- name: eating
  calorie: 1294.9
  date: '2021-03-02'
- name: sporting
  calorie: -2375
  date: '2023-04-27'
- name: sleeping
  calorie: -420.5
  date: '2023-05-15'
```

#### Example 2. TOML to XML

```shell
$ jf test/example.toml -f xml
```

Output:

```xml
<?xml version="1.0" ?>
<root>
    <name>Bob</name>
    <age>23</age>
    <gender>纯爷们</gender>
    <money>3.1415926</money>
    <actions>
        <name>eating</name>
        <calorie>1294.9</calorie>
        <date>2021-03-02</date>
    </actions>
    <actions>
        <name>sporting</name>
        <calorie>-2375</calorie>
        <date>2023-04-27</date>
    </actions>
    <actions>
        <name>sleeping</name>
        <calorie>-420.5</calorie>
        <date>2023-05-15</date>
    </actions>
</root>
```


### 5. Diff Comparison

In development, we often need to compare differences between some data or configurations. For example, compare the return results of an API when passing in different parameters, or compare the differences between system configuration files in different formats by operations personnel.

jsonfmt supports various diff-tools by default, such as `diff`, `vimdiff`, `git`, `code`, `kdiff3`, `meld`, and also supports `WinMerge` and `fc` on Windows, and other tools can also be supported through the `-D` option.

By default, jsonfmt will first check if git is installed on the computer. If git is available, jsonfmt will call `git config --global diff.tool` to read the configured diff-tool. If it's not set, it will use the default diff-tool of git for processing. If git is not available, it will search in the order of `code`, `kdiff3`, `meld`, `vimdiff`, `diff`, `WinMerge`, `fc`. If no available diff-tool is found, jsonfmt will exit with an error.

In DiffMode, jsonfmt will first format the data to be compared (at this time, the `-s` option will be automatically enabled), and save the result to a temporary file, and then call the specified tool for diff comparison.

#### Example 1: Compare two JSON files

```shell
$ jf -d test/example.json test/another.json
```

Output:

```diff
--- /tmp/.../jf-jjn86s7r_example.json     2024-03-23 18:22:00
+++ /tmp/.../jf-vik3bqsu_another.json     2024-03-23 18:22:00
@@ -3,21 +3,16 @@
     {
       "calorie": 1294.9,
       "date": "2021-03-02",
-      "name": "eating"
+      "name": "thinking"
     },
     {
-      "calorie": -2375,
-      "date": "2023-04-27",
-      "name": "sporting"
-    },
-    {
       "calorie": -420.5,
       "date": "2023-05-15",
       "name": "sleeping"
     }
   ],
   "age": 23,
-  "gender": "纯爷们",
+  "gender": "male",
   "money": 3.1415926,
-  "name": "Bob"
+  "name": "Tom"
 }
```

#### Example 2: Specify diff-tool with `-D`

The `-D DIFFTOOL` option can specify a diff comparison tool. As long as its command format matches `command [options] file1 file2`, it doesn't matter whether it's in jsonfmt's default supported tool list or not.

```shell
$ jf -D sdiff test/example.json test/another.json
```

Output:

```
{                                   {
  "actions": [                        "actions": [
    {                                   {
      "calorie": 1294.9,                  "calorie": 1294.9,
      "date": "2021-03-02",               "date": "2021-03-02",
      "name": "eating"         |          "name": "thinking"
    },                                  },
    {                                   {
      "calorie": -2375,        <
      "date": "2023-04-27",    <
      "name": "sporting"       <
    },                         <
    {                          <
      "calorie": -420.5,                  "calorie": -420.5,
      "date": "2023-05-15",               "date": "2023-05-15",
      "name": "sleeping"                  "name": "sleeping"
    }                                   }
  ],                                  ],
  "age": 23,                          "age": 23,
  "gender": "纯爷们",          |      "gender": "male",
  "money": 3.1415926,                 "money": 3.1415926,
  "name": "Bob"                |      "name": "Tom"
}                                   }
```

#### Example 3: Specify options for the selected tool

If you need to pass parameters to the diff-tool, you can use `-D 'DIFFTOOL OPTIONS'`.

```shell
$ jf -D 'diff --ignore-case --color=always' test/example.json test/another.json
```

Output:

```diff
6c6
<       "name": "eating"
---
>       "name": "thinking"
9,13d8
<       "calorie": -2375,
<       "date": "2023-04-27",
<       "name": "sporting"
<     },
<     {
20c15
<   "gender": "纯爷们",
---
>   "gender": "male",
22c17
<   "name": "Bob"
---
>   "name": "Tom"
```

#### Example 4: Compare data in different formats

For data from different sources, their formats, indentation, and key order may be different. In this case, you can use `-i` and `-f` together for diff comparison.

```shell
$ jf -d -i 4 -f toml test/example.toml test/another.json
```

Output:

```diff
--- /var/.../jf-qw9vm33n_example.toml     2024-03-23 18:29:17
+++ /var/.../jf-dqb_fl4x_another.json     2024-03-23 18:29:17
@@ -1,18 +1,13 @@
 age = 23
-gender = "纯爷们"
+gender = "male"
 money = 3.1415926
-name = "Bob"
+name = "Tom"
 [[actions]]
 calorie = 1294.9
 date = "2021-03-02"
-name = "eating"
+name = "thinking"

 [[actions]]
-calorie = -2375
-date = "2023-04-27"
-name = "sporting"
-
-[[actions]]
 calorie = -420.5
 date = "2023-05-15"
 name = "sleeping"
```

### 6. Handle Large JSON Data Conveniently

Very often, JSON data from program interfaces is very large, which makes it difficult for us to read, debug, and process. jsonfmt provides four ways to handle large JSON data:

- Use JMESPath or JSONPath to read part of the content ([already covered in the previous section](#3-extract-partial-content-from-json-data))
- [Use pager mode to view larger JSON data](#use-pager-mode-to-view-larger-json-data)
- [Show an overview of large JSON data](#show-an-overview-of-large-json-data)
- [Copy the processing result to the clipboard](#copy-the-processing-result-to-the-clipboard)

#### Use pager mode to view larger JSON data

Pager mode is similar to the `more` command. When the JSON data is too large to be fully displayed in the window area, *jsonfmt* will automatically display the result in pager mode.

The operations in pager mode are the same as the `more` command:

| Key                                           | Description                    |
|-----------------------------------------------|--------------------------------|
| <kbd>j</kbd>                                  | Move forward one line          |
| <kbd>k</kbd>                                  | Move backward one line         |
| <kbd>f</kbd> or <kbd>ctrl</kbd>+<kbd>f</kbd>  | Move forward one page          |
| <kbd>b</kbd>  or <kbd>ctrl</kbd>+<kbd>b</kbd> | Move backward one page         |
| <kbd>g</kbd>                                  | Jump to the top of the page    |
| <kbd>G</kbd>                                  | Jump to the bottom of the page |
| <kbd>/</kbd>                                  | Search mode                    |
| <kbd>q</kbd>                                  | Exit pager mode                |

The return value of this API below is a large JSON data, you can paste this command into the terminal to try the pager mode:

```shell
$ curl -s https://jsonplaceholder.typicode.com/users | jf
```

#### Show an overview of large JSON data

Sometimes we only want to see an overview of the JSON data without caring about the details. In this case, you can use the `-o` option. It will clear the sublists in the JSON, and replace the strings to `"..."` to show the overview.

If the root node of the JSON data is a list, only its first child element will be preserved in the overview.

```shell
$ jf -o test/example.json
```

Output:

```json
{
    "name": "...",
    "age": 23,
    "gender": "...",
    "money": 3.1415926,
    "actions": []
}
```

#### Copy the processing result to the clipboard

If you want to paste the processed result into a file, but the output printed in the terminal exceeds one page, it may be difficult to copy. In this case, you can use the `-C` option to automatically copy the result to the clipboard.

```shell
$ jf -C test/example.json
```

After completing the above operation, you can use <kbd>ctrl</kbd>+<kbd>v</kbd> or <kbd>cmd</kbd>+<kbd>v</kbd> to paste the result into other documents.

<div style="color: orange"><strong>Note:</strong></div>

When processing multiple targets at the same time, such as: `jf -C file1 file2 file3 ...`, jsonfmt will copy the processing results of all files to the clipboard, with two newline characters `'\n\n'` separating multiple results.

### 7. Modify Values in Input Data

When you need to change some content in the input document, use the `--set` and `--pop` options.

The format is `--set 'key=value'`. If you need to modify multiple values, you can separate them with `;`, like this: `--set 'k1=v1;k2=v2'`. If the key-value pair does not exist, it will be added.

For items in a list, use `key[i]` or `key.i` to specify. If the index is greater or equal to the number of elements, the value will be appended.

#### Add key-value pairs

```shell
# Add country = China, and append an item to actions
$ jf --set 'country=China; actions[3]={"name": "drinking"}' test/example.json
```

Output:

```json
{
    "name": "Bob",
    "age": 23,
    "gender": "纯爷们",
    "money": 3.1415926,
    "actions": [
        {
            "name": "eating",
            "calorie": 1294.9,
            "date": "2021-03-02"
        },
        {
            "name": "sporting",
            "calorie": -2375,
            "date": "2023-04-27"
        },
        {
            "name": "sleeping",
            "calorie": -420.5,
            "date": "2023-05-15"
        },
        {
            "name": "drinking"
        }
    ],
    "country": "China"
}
```

#### Modify values

```shell
# Modify money and actions[1]["name"]
$ jf --set 'money=1000; actions[1].name=swim' test/example.json
```

Output:

```json
{
    "name": "Bob",
    "age": 23,
    "gender": "纯爷们",
    "money": 1000,
    "actions": [
        {
            "name": "eating",
            "calorie": 1294.9,
            "date": "2021-03-02"
        },
        {
            "name": "swim",
            "calorie": -2375,
            "date": "2023-04-27"
        },
        {
            "name": "sleeping",
            "calorie": -420.5,
            "date": "2023-05-15"
        }
    ]
}
```

#### Delete key-value pairs

```shell
# Delete gender and actions[1]
$ jf --pop 'gender; actions[1]' test/example.json
```

Output:

```json
{
    "name": "Bob",
    "age": 23,
    "money": 3.1415926,
    "actions": [
        {
            "name": "eating",
            "calorie": 1294.9,
            "date": "2021-03-02"
        },
        {
            "name": "sleeping",
            "calorie": -420.5,
            "date": "2023-05-15"
        }
    ]
}
```

Of course, you can also use `--set` and `--pop` at the same time:

```shell
jf --set 'skills=["Django","Flask"];money=1000' --pop 'gender;actions[1]' test/example.json
```

<div style="color: orange"><strong>Note:</strong></div>
The above command will not modify the original JSON file. If you want to do so, see below.

### 8. Output to File

jsonfmt does not provide a dedicated option to write the processing result to a file. Because you can easily handle this by using the terminal's redirection symbol `>`, which is supported on both Linux and Windows.

```shell
$ jf -si 4 test/example.json > formatted.json
```

If you need to overwrite the processed result to the original file, you can use the `-O` option:

```shell
# Sort by object keys, set indentation to 4 spaces, set the name value to Alex, and write the final result to the original file
$ jf -s -i 4 --set 'name=Alex' -O test/example.json
```

## TODO

- [ ] Add URL support to directly compare data from two APIs
- [ ] Add INI format support
- [ ] Add merge mode to combine multiple JSON or other formatted data into one
