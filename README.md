# JSON Formator

`jsonfmt` is a JSON object formatting tool.

## Features

1. Print the JSON object in pretty format from files or stdin.
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

     - `-h, --help `:  show this help message and exit
     - `-c`:  compression the json object in the files or stdin.
     - `-O`:  overwrite the formated json object into the json file.
     - `-p JSONPATH`:  output part of json object via the json path (Use `/` to separate different levels).


## Example

1. Pretty print from json file.

    ```json
    $ jsonfmt example.json

     [
          {
               "attr": "original",
               "banner": "https://img.example.net/u/9172583_50.png",
               "date": "2023年04月23日 01:29",
               "height": 2585,
               "id": 107429,
               "istyle": "0",
               "itype": {
                    "a": false,
                    "b": false,
                    "d": false,
                    "f": false,
                    "l": false,
                    "y": false
               },
               "name": "ももこ",
               ...
          },
          ...
     ]
    ```

2. Compress the JSON string from stdin.

     ```json
     $ echo '{
          "name": "hello",
          "age": 21,
          "item": ["pen", "ruler", "phone"]
     }' | jsonfmt -c

     {"age":21,"item":["pen","ruler","phone"],"name":"hello"}
     ```

3. Use json path.

     ```json
     $ jsonfmt -p '2/tags' example.json

     [
          "オリジナル",
          "がんばれ同期ちゃん"
     ]
     ```
