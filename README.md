# JSON Formator

**jsonfmt** is a json object formatting tool.

## Features

1. Print the json object in pretty format from files or stdin.
2. Compress the json object into a single line without spaces.
3. Output part of a large json object via jsonpath.

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
     - `-c`: compression the json object in the files or stdin.
     - `-O`: overwrite to the json file.
     - `-p JSONPATH`: output part of json object via jsonpath.
     - `-v`: show the version.


## Example

In the file example.json there is a compressed json object.

1. Pretty print from json file.

     ```shell
     $ jsonfmt example.json
     ```

     ouput:
     ```json
     {
          "age": 23,
          "gender": "male",
          "history": [
               {
                    "action": "eat",
                    "date": "2021-03-02",
                    "items": [
                         {
                              "bar": 222,
                              "foo": 111
                         },
                         {
                              "bar": -222,
                              "foo": -111
                         }
                    ]
               },
               {
                    "action": "drink",
                    "date": "2022-11-01",
                    "items": [
                         {
                              "bar": 444,
                              "foo": 333
                         },
                         {
                              "bar": -444,
                              "foo": -333
                         }
                    ]
               },
               {
                    "action": "walk",
                    "date": "2023-04-27",
                    "items": [
                         {
                              "bar": 666,
                              "foo": 555
                         },
                         {
                              "bar": -666,
                              "foo": -555
                         }
                    ]
               }
          ],
          "name": "bob"
     }
    ```

     Of course, you can use the `-O` parameter to overwrite the file with the result:

     ```shell
     $ jsonfmt -O example.json
     ```

2. Compress the json string from stdin.

     ```shell
     $ echo '{
          "name": "alex",
          "age": 21,
          "items": ["pen", "ruler", "phone"]
     }' | jsonfmt -c
     ```

     ouput:
     ```json
     {"age":21,"items":["pen","ruler","phone"],"name":"alex"}
     ```

3. Use jsonpath to match part of a json object.

     **jsonfmt** uses a simplified jsonpath syntax.

     - It matches json objects starting from the root node.
     - You can use keys to match dictionaries and indexes to match lists, and use `/` to separate different levels.

          ```shell
          $ jsonfmt -p 'history/0/date' example.json
          ```

          ouput:
          ```json
          "2021-03-02"
          ```

     - If you want to match all items in a list, just use `*` to match.

          ```shell
          $ jsonfmt -p 'history/*/action' example.json
          ```

          ouput:
          ```json
          [
               "eat",
               "drink",
               "walk"
          ]
          ```
