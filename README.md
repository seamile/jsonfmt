# JSON Formator

![PyPI - Downloads](https://img.shields.io/pypi/dm/jsonfmt?label=Install&color=green)
![PyPI](https://img.shields.io/pypi/v/jsonfmt?color=9cf)
![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/seamile/jsonfmt/python-package.yml?branch=main&label=build&logo=python)


**jsonfmt** is a JSON object formatting tool.

It has the following features:

1. Print the JSON object with **hightlight** and **pretty format** from files or stdin.
2. Compress the JSON object into a single line without spaces.
3. Output part of a large JSON object via jsonpath.

## Install

```shell
$ pip install jsonfmt
```

## Usage

```shell
$ jsonfmt [-h] [-c] [-O] [-p JSONPATH] [json_files ...]
```

- positional arguments:

     - `json_files`   the json files that will be processed

- options:

     - `-h, --help`: show this help message and exit.
     - `-c`: compression the JSON object in the files or stdin.
     - `-e`: escape non-ASCII characters.
     - `-i INDENT`: number of spaces to use for indentation. (default: 4)
     - `-O`: overwrite to the json file.
     - `-p JSONPATH`: output part of JSON object via jsonpath.
     - `-v`: show the version.


## Example

In the file example.json there is a compressed JSON object.

1. Pretty print from json file.

     ```shell
     $ jsonfmt example.json
     ```

     Output:
     ```json
     {
          "age": 23,
          "gender": "纯爷们",
          "history": [
               {
                    "action": "eat",
                    "date": "2021-03-02",
                    "items": [
                         {
                              "calorie": 294.9,
                              "name": "hamburger"
                         },
                         {
                              "calorie": 266,
                              "name": "pizza"
                         }
                    ]
               },
               {
                    "action": "drink",
                    "date": "2022-11-01",
                    "items": [
                         {
                              "calorie": 37.5,
                              "name": "Coca Cola"
                         },
                         {
                              "calorie": 54.5,
                              "name": "juice"
                         }
                    ]
               },
               {
                    "action": "sport",
                    "date": "2023-04-27",
                    "items": [
                         {
                              "calorie": -375,
                              "name": "running"
                         },
                         {
                              "calorie": -350,
                              "name": "swimming"
                         }
                    ]
               }
          ],
          "name": "Bob"
     }
    ```

     Of course, you can use the `-O` parameter to overwrite the file with the result:

     ```shell
     $ jsonfmt -O example.json
     ```


2. Format a JSON object from stdin via pipeline.

     ```shell
     $ curl https://raw.githubusercontent.com/seamile/jsonfmt/main/example.json | jsonfmt
     ```

     Output: Ditto.


3. Compress the JSON object.

     ```shell
     $ echo '{
          "name": "alex",
          "age": 21,
          "items": ["pen", "ruler", "phone"]
     }' | jsonfmt -c
     ```

     Output:
     ```json
     {"age":21,"items":["pen","ruler","phone"],"name":"alex"}
     ```

4. Use jsonpath to match part of a JSON object.

     **jsonfmt** uses a simplified jsonpath syntax.

     - It matches JSON objects starting from the root node.
     - You can use keys to match dictionaries and indexes to match lists, and use `/` to separate different levels.

          ```shell
          $ jsonfmt -p 'history/0/date' example.json
          ```

          Output:
          ```json
          "2021-03-02"
          ```

     - If you want to match all items in a list, just use `*` to match.

          ```shell
          $ jsonfmt -p 'history/*/items/*/name' example.json
          ```

          Output:
          ```json
          [
               [
                    "hamburger",
                    "pizza"
               ],
               [
                    "Coca Cola",
                    "juice"
               ],
               [
                    "running",
                    "swimming"
               ]
          ]
          ```
