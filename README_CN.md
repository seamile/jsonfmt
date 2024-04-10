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

</div>

### <div align="center"><a href="README.md">🇬🇧 English</a></div>

**_jsonfmt_**（JSON Formatter）是一款简单而强大的 JSON 处理工具。

众所周知，Python 自身已经内置了一个用于格式化 JSON 数据的工具：`python -m json.tool`。但是它的功能过于简单，因此 **jsonfmt** 在此基础上做了很多实用的扩展：

🎨 它不仅可以用来漂亮的打印 JSON 数据，

🔄 也可以将 JSON、TOML、XML、YAML 数据进行互相转化，

🔎 还可以通过 JMESPATH 或 JSONPATH 来提取 JSON 中的内容。

👀 您甚至可以通过 **jsonfmt** 来比较两个 JSON 或其他格式的数据之间的差异。


- [快速上手](#快速上手)
    - [安装](#安装)
    - [用法](#用法)
- [使用指南](#使用指南)
    - [1. 漂亮地打印 JSON 数据](#1-漂亮地打印-json-数据)
    - [2. 最小化 JSON 数据](#2-最小化-json-数据)
    - [3. 提取 JSON 数据的部分内容](#3-提取-json-数据的部分内容)
    - [4. 格式转换](#4-格式转换)
    - [5. 差异对比](#5-差异对比)
    - [6. 方便的处理大型 JSON 数据](#6-方便的处理大型-json-数据)
    - [7. 修改输入数据中的某些值](#7-修改输入数据中的某些值)
    - [8. 输出到文件](#8-输出到文件)
- [TODO](#todo)


## 快速上手

### 安装

```shell
$ pip install jsonfmt
```

### 用法

1. 处理文件中的数据。

  ```shell
  $ jf [可选参数] [数据文件 ...]
  ```

2. 处理“标准输入”中的数据。

  ```shell
  $ echo '{"hello": "world"}' | jf [可选参数]
  ```

**位置参数**

`files`: 要处理的数据文件，支持 JSON / TOML / XML / YAML 格式。

**可选参数**

- `-h`: 显示帮助文档。
- `-C`: 复制模式，此模式会将处理结果复制到剪贴板。
- `-d`: 对比模式. 此模式可以对传入的两个数据进行差异对比。
- `-D DIFFTOOL`: 与“对比模式”类似。你可以指定一个工具来进行差异对比。
- `-o`: 概览模式，可以显示数据结构的概览，可以用来快速了解较大的数据。
- `-O`: 覆盖模式，会将处理后的内容覆盖到原文件。
- `-c`: 删除 JSON 中的所有空白字符（对其他数据格式无效）
- `-e`: 将所有字符转义成 ASCII 码
- `-f`: 输出格式（默认值：与传入的数据格式相同，可选项：`json` / `toml` / `xml` / `yaml`）
- `-i`: 缩进的空格数（默认值：2，范围：0~8，设置 t 时会以 <kbd>Tab</kbd> 作为缩进符）
- `-l`: 提取数据时的查询语言（默认：自动识别，可选项：jmespath / jsonpath）
- `-p QUERYPATH`: JMESPath 或 JSONPath 查询路径
- `-s`: 按键的字母顺序对数据中的字典进行排序
- `--set 'foo.k1=v1;k2[i]=v2'`: 要添加或修改的键值对（多个值用“;”分隔）
- `--pop 'k1;foo.k2;k3[i]'`: 通过键指定要删除的键值对（多个值用“;”分隔）
- `-v`: 显示版本号


## 使用指南

为了演示 jsonfmt 的功能，我们需要先创建一份测试数据，并将其保存到文件 example.json 中。文件内容如下所示：

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

然后，再将这份数据转换为 TOML、XML 和 YAML 格式，分别保存到文件 example.toml、example.xml 和 example.yaml 中。

这些数据文件可以在源码的 *test* 文件夹中找到:

```
test/
|- example.json
|- example.toml
|- example.xml
|- example.yaml
```

### 1. 漂亮地打印 JSON 数据

#### 语法高亮和缩进

jsonfmt 默认的工作模式就是对数据进行格式化处理，并以带有语法高亮的形式进行打印。

选项 `-i` 可以指定缩进的空格数量。默认情况下，缩进为 2 个空格，允许的空格数介于 0 到 8 之间。如果想要使用制表符 <kbd>tab</kbd> 作为缩进，可将其设置为 `t`。

选项 `-s` 用于按字典键名顺序对输出结果进行排序。

如果 JSON 数据中有一些非 ASCII 字符，您可以使用 `-e` 对它们进行转义。

```shell
$ jf -s -i 4 test/example.json
```

输出：

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

#### 从管道读取 JSON

如果要处理的数据来自于其他命令的输出，这时只需使用管道 `|` 连接两个命令，然后从“标准输入”中取即可。

```shell
$ curl -s https://jsonplaceholder.typicode.com/posts/1 | jf -i 4
```

输出：

```json
{
    "userId": 1,
    "id": 1,
    "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
    "body": "quia et suscipit\nsuscipit recusandae consequuntur expedita et cum\nrep..."
}

```

### 2. 最小化 JSON 数据

选项 `-c` 可用于删除所有的空白和换行符，将 JSON 数据压缩成单行。

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

输出：

```json
{"name":"alex","age":21,"items":["pen","phone"]}
```

### 3. 提取 JSON 数据的部分内容

jsonfmt 同时使用 [**JMESPath**](https://jmespath.org/) 和 [**JSONPath**](https://datatracker.ietf.org/doc/id/draft-goessner-dispatch-jsonpath-00.html) 作为其查询语言。

**JMESPath**（JSON Meta Language for Expression Path）是由 AWS 推出的一种查询语言，用于处理JSON数据。在众多 JSON 查询语言中，JMESPath 似乎是使用最广、增长最快、评价最好的解决方案。它比 [**jq**](https://jqlang.github.io/jq/) 的语法更简洁、更通用，比 JSONPath 的功能更丰富、更强大，因此我更倾向于使用它作为主要的 JSON 查询语言。

JMESPath 可以优雅地使用简单的语法从 JSON 数据中提取一部分内容，也可以将过滤后的数据组成一个新的对象或数组。JMESPath 的官方教程在[这里](https://jmespath.org/tutorial.html)。

#### JMESPath 示例

- 提取 *example.json* 中 `actions` 的第一项：

    ```shell
    $ jf -p 'actions[0]' test/example.json
    ```

    输出：

    ```json
    {
        "name": "eating",
        "calorie": 1294.9,
        "date": "2021-03-02"
    }
    ```

- 过滤 `actions` 中所有 `calorie < 0` 的项。

    ```shell
    # 此处的 `0` 表示 0 是一个数字
    $ jf -p 'actions[?calorie<`0`]' test/example.json
    ```

    输出：

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

- 显示所有键和 `actions` 的长度。

    ```shell
    $ jf -p '{all_keys:keys(@), actions_len:length(actions)}' test/example.json
    ```

    输出：

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

- 按 `actions` 中每一项的  `calorie` 值进行排序，并将结果定义成一个新字典。

    ```shell
    $ jf -p 'sort_by(actions, &calorie)[].{foo: name, bar:calorie}' test/example.json
    ```

    输出：

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

[更多 JMESPath 示例](https://jmespath.org/examples.html)。

#### JSONPath 示例

JSONPath 的设计灵感来源于 XPath。因此它可以像 XPath 那样通过类似于路径表达式的方式精准地定位到 JSON 文档中的任意元素，从而实现对复杂嵌套数据的高效检索、筛选与操作。

不同于 XML 的标签层级结构，JSONPath 针对 JSON 的键值对和数组进行了特殊处理，使得用户可以方便地访问多级对象属性、遍历对象和数组，以及根据条件过滤数据。

有些使用 JMESPath 难以处理的查询，JSONPath 却可以很轻松的实现。

- 通过相对路径过滤所有 `name` 字段:

    ```shell
    # 使用 -l 指定的查询语言为 JSONPath
    $ jf -l jsonpath -p '$..name' test/example.json
    ```

    输出：

    ```json
    [
        "Bob",
        "eating",
        "sporting",
        "sleeping"
    ]
    ```

在执行查询时，您可以不指定 `-l` 选项。jsonfmt 会先尝试使用 JMESPath 语法去解析 `-p QUERYPATH`

#### 查询 TOML、XML 和 YAML

jsonfmt 的众多强大功能之一就是，您可以使用与 JSON 完全同样的方式来处理 TOML、XML 和 YAML，并任意转换结果的格式。甚至可以在单个命令中同时处理这四种格式。

- 从 toml 文件读取数据，并以 YAML 格式输出

    ```shell
    $ jf -p '{all_keys:keys(@), actions_len:length(actions)}' test/example.toml -f yaml
    ```

    输出：

    ```yaml
    all_keys:
    - name
    - age
    - gender
    - money
    - actions
    actions_len: 3
    ```

- 同时处理四种格式

    ```shell
    $ jf -p 'actions[0]' test/example.json test/example.toml test/example.xml test/example.yaml
    ```

    输出：

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


### 4. 格式转换

*jsonfmt* 支持 JSON、TOML、XML 和 YAML 格式的处理。每种格式都可以通过指定 "-f" 选项转换为其他格式。

<div style="color: orange"><strong>注意:</strong></div>

1. TOML 中不存在 `null` 值。因此从其他格式转换为 TOML 时，所有的 null 值都将被删除。
2. XML 不支持多维数组。所以在向 XML 格式转换时，如果原数据中存在多维数组，则会产生错误的数据。

#### 例1. JSON 转换为 YAML

```shell
$ jf test/example.json -f yaml
```

输出：

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

#### 例2. TOML 转换为 XML

```shell
$ jf test/example.toml -f xml
```

输出：

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


### 5. 差异对比

在开发中，我们经常需要对一些数据或者配置进行差异对比。比如对比某个 API 在传入不同参数时的返回结果，或者运维人员对比某个系统不同格式的配置文件之间的差异。

jsonfmt 默认支持多种差异对比工具，如：`diff`、`vimdiff`、`git`、`code`、`kdiff3`、`meld`，也支持 Windows 上的 `WinMerge` 和 `fc`，还可以通过 `-D` 选项来支持其他工具。

默认情况下，jsonfmt 会首先检查电脑上是否安装了 git。如果 git 可用，jsonfmt 会调用 `git config --global diff.tool` 读取其配置的对比工具。如果未设置该项则使用 git 默认的差异对比工具进行处理。如果电脑上没有安装 git，则会按照 `code`、`kdiff3`、`meld`、`vimdiff`、`diff`、`WinMerge`、`fc` 的顺序进行查找。如果没有找到可用的差异对比工具，jsonfmt 会报错退出。

在差异对比模式下，jsonfmt 会先将需要对比的数据进行格式化处理（此时 `-s` 选项会被自动激活），并将结果保存到临时文件中，然后再调用指定的工具进行差异对比。

#### 例1. 对比两个 JSON 文件

```shell
$ jf -d test/example.json test/another.json
```

输出：

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

#### 例2. 通过 `-D` 选定对比工具

`-D DIFFTOOL` 选项可以指定一款差异对比工具。只要其命令格式满足 `command [options] file1 file2` 即可，无论它是否在 jsonfmt 默认支持的工具列表中。

```shell
$ jf -D sdiff test/example.json test/another.json
```

输出：

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

#### 例3. 为选定的工具指定参数

如果需要向差异对比工具传递参数，可以使用 `-D 'DIFFTOOL OPTIONS'` 来操作。

```shell
$ jf -D 'diff --ignore-case --color=always' test/example.json test/another.json
```

输出：

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

#### 例4. 对比不同格式的数据

对于不同来源的数据，其格式、缩进，以及键的顺序可能都不一样，这时可以使用 `-i`、`-f` 配合来进行差异对比。

```shell
$ jf -d -i 4 -f toml test/example.toml test/another.json
```

输出：

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


### 6. 方便的处理大型 JSON 数据

很多时候来自于程序接口的 JSON 数据非常大，这会给我们阅读、调试、处理带来很多困难。jsonfmt 提供了四种方式来处理大型 JSON 数据：

- 使用 JMESPath 或 JSONPath 读取一部分内容（[前文已经做过介绍](#3-提取-json-数据的部分内容)）
- [使用分页模式查看较大的 JSON 数据](#使用分页模式查看较大的-json-数据)
- [显示大型 JSON 数据的概览](#显示大型-json-数据的概览)
- [将处理结果复制到剪贴板](#将处理结果复制到剪贴板)

#### 使用分页模式查看较大的 JSON 数据

分页模式类似于 `more` 命令。当 JSON 数据过大而无法在窗口显示区域内完全显示时，*jsonfmt* 将自动以分页模式呈现结果。

分页模式的操作与 `more` 命令相同:

| 键                                            | 描述         |
|-----------------------------------------------|--------------|
| <kbd>j</kbd>                                  | 前进一行     |
| <kbd>k</kbd>                                  | 后退一行     |
| <kbd>f</kbd> 或 <kbd>ctrl</kbd>+<kbd>f</kbd>  | 前进一页     |
| <kbd>b</kbd>  或 <kbd>ctrl</kbd>+<kbd>b</kbd> | 后退一页     |
| <kbd>g</kbd>                                  | 跳到页面顶部 |
| <kbd>G</kbd>                                  | 跳到页面底部 |
| <kbd>/</kbd>                                  | 搜索模式     |
| <kbd>q</kbd>                                  | 退出分页模式 |

下面这个 API 的返回值是一个大型 JSON 数据，您可以将此命令粘贴到终端以尝试分页模式:

```shell
$ curl -s https://jsonplaceholder.typicode.com/users | jf
```

#### 显示大型 JSON 数据的概览

有时我们只想看到 JSON 数据的概览而不关心具体细节，这时可以使用 `-o` 选项。

它将清除 JSON 中的子列表，并将字符串修改为 `"..."` 以显示概览。

如果 JSON 数据的根节点是一个列表，概览中仅保留它的第一个子元素。

```shell
$ jf -o test/example.json
```

输出：

```json
{
    "name": "...",
    "age": 23,
    "gender": "...",
    "money": 3.1415926,
    "actions": []
}
```

#### 将处理结果复制到剪贴板

如果您想将处理后的结果粘贴到文件中，但终端中打印的内容超过了一页时，复制起来会比较困难。此时，您可以通过 `-C` 选项，将结果自动复制到剪贴板。

```shell
$ jf -C test/example.json
```

完成上述操作后，您可以使用 <kbd>ctrl</kbd>+<kbd>v</kbd> 或 <kbd>cmd</kbd>+<kbd>v</kbd> 将结果粘贴到其他文档中。

<div style="color: orange"><strong>注意:</strong></div>

当同时处理多个目标时，比如：`jf -C file1 file2 file3 ...`，jsonfmt 会将所有文件的处理结果都复制到剪贴板，多个结果之间使用两个换行符 '\n\n' 进行分隔。


### 7. 修改输入数据中的某些值

当您需要更改输入文档中的某些内容时，请使用 `--set` 和 `--pop` 选项。

格式为 `--set 'key=value'`。如果需要修改多个值，可以使用 `;` 分隔：`--set 'k1=v1;k2=v2'`。如果键值对不存在，则会被添加。

对于列表中的项目，请使用 `key[i]` 或 `key.i` 指定。如果索引大于或等于元素个数,则值将被追加。

#### 添加键值对

```shell
# 添加 country = China，并为 actions 追加一项
$ jf --set 'country=China; actions[3]={"name": "drinking"}' test/example.json
```

输出：

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

#### 修改值

```shell
# 修改 money 和 actions[1]["name"]
$ jf --set 'money=1000; actions[1].name=swim' test/example.json
```

输出：

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

#### 删除键值对

```shell
# 删除 gender 和 actions[1]
$ jf --pop 'gender; actions[1]' test/example.json
```

输出：

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

当然，您也可以同时使用 `--set` 和 `--pop`：

```shell
jf --set 'skills=["Django","Flask"];money=1000' --pop 'gender;actions[1]' test/example.json
```

<div style="color: orange"><strong>注意:</strong></div>
上述命令不会修改原始 JSON 文件。如果您想这样做，请继续阅读下文。


### 8. 输出到文件

jsonfmt 并没有专门提供将处理结果写入到文件的选项。因为使用终端的重定向符号 `>` 可以很方便的处理这个事情，而且不管是 Linux 还是 Windows 都支持这一操作。

```shell
$ jf -si 4 test/example.json > formatted.json
```

如果需要将处理结果覆盖到原文件，可以使用 `-O` 选项：

```shell
# 按照对象的 key 进行排序，缩进设置为 4 个空格，将 name 的值设置为 Alex，并将最终结果写入到原文件中
$ jf -s -i 4 --set 'name=Alex' -O test/example.json
```


## TODO

- [ ] 增加 URL 支持，可以直接对比来自两个 API 的数据
- [ ] 增加 INI 格式支持
- [ ] 增加 merge 模式，将多个 JSON 或其他格式的数据按 key 进行合并
