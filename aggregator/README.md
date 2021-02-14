# 集計ツール

本ツールは Context Broker に格納された covid19 データを加工集計し、
FIWARE 版コロナ対策サイトで使用するためのデータを生成します。

## 動作環境

変換ツールはpython3で記述されいます。python3が導入された環境で利用できます。また、ymlファイルを読み込むために、`pyyaml`を使用します。事前にインストールしてくさい。

```console
cd aggregator/
pip install -r requirements.txt
```

## 使用方法

```console
./aggregate.py --help
usage: aggregator.py [-h] [-m MCODE] [-t TYPE] [-c CONFIG]

Entity aggregation tool.

optional arguments:
  -h, --help            show this help message and exit
  -m MCODE, --mcode MCODE
                        Municipality code.
  -t TYPE, --type TYPE  Aggregate type.
  -c CONFIG, --config CONFIG
                        Config file.

Aggregate types:
PatientsSummary
PatientsDaily
PatientsList
TestPeopleDaily
TestCountDaily
ConfirmNegativeDaily
CallCenterDaily
```

| 項目                    | 説明                             |
| ----------------------- | -------------------------------- |
| -h, --help              | コマンドのヘルプを表示             |
| -m MCODE, --mcode MCODE | 地方公共団体コードを指定(オプション) |
| -t TYPE, --type TYPE    | 集計するデータタイプを指定(後述)    |
| -c CONFIG, --config     | 設定ファイルを指定(JSONまたはyaml) |


## 設定ファイルについて

本ツールの動作設定は、yamlで記述します。

設定ファイルは、コマンドの `-c`  オプションで指定します。

`-c` オプションで設定ファイルを指定しなかった場合は、
カレントディレクトリ内の `config.json` を読み込みます。

 yamlの場合は以下の設定を記述します。

- Broker の設定
- 全国地方公共団体コード
- 集計を行う項目

JSONの場合は以下の設定を記述します。

- Broker の設定

JSONの場合は他の設定項目はコマンド引数で指定します。
JSONの場合は、引数 `-m` と `-t` は必須です。

### yaml での設定

yaml での設定ファイル例
```yaml
version: "1"

code: "401005"

broker:
  type: "v2"
  url: "http://broker"
  service: "covid19"
  path: "/path"
  token: "api_token"
  context: "http://example.com/context.jsonldh"

aggregate:
  - "TestPeopleDaily"
  - "TestCountDaily"
  - "ConfirmNegativeDaily"
  - "CallCenterDaily"
  - "PatientsDaily"
  - "PatientsList"
  - "PatientsSummary"
```

以下の内容を設定します。

#### version

設定ファイルのバージョンを指定します。 "1" を入力してください。(必須)

#### code

全国地方公共団体コードを設定します。(必須)

#### broker

Context Broker の設定を行います。
設定内容は以下の通りです。

| 設定名  | 説明                                                                         |
| ------- | ---------------------------------------------------------------------------- |
| type    | NGSI のタイプを指定。「v2」もしくは「ld」を指定 (オプション/ デフォルト: v2) |
| url     | Context Broker の URL を指定 (必須)                                          |
| service | Context Broker の サービス(テナント)を指定 (オプション)                      |
| path    | Context Broker の パスを指定 (オプション)                                    |
| token   | Context Broker にアクセスするためのトークンを指定 (オプション)               |
| context | NGSI タイプが「ld」の時に使用するコンテキストの URL を指定 (オプション)      |

#### aggregate

集計データタイプを指定します。複数のタイプをまとめて指定できます。

| データタイプ          | 説明                           |
| --------------------- | ------------------------------ |
| PatientsSummary       | 陽性患者サマリ集計             |
| PatientsDaily         | 陽性患者日別集計               |
| PatientsList          | 陽性患者一覧集計               |
| TestPeopleDaily       | 検査実施人数日別集計           |
| TestCountDaily        | 検査実施件数日別集計           |
| ConfirmNegativeDaily  | 陽性確認数日別集計             |
| CallCenterDaily       | コールセンター相談件数日別集計 |


### Context Broker の設定

Context Broker の設定については、以下の環境変数を使って設定することもできます。

| 設定名         | 説明                                                                         |
| -------------- | ---------------------------------------------------------------------------- |
| BROKER_VERSION | NGSI のタイプを指定。「v2」もしくは「ld」を指定 (オプション/ デフォルト: v2) |
| BROKER_URL     | Context Broker の URL を指定 (必須)                                          |
| BROKER_SERVICE | Context Broker の サービス(テナント)を指定 (オプション)                      |
| BROKER_PATH    | Context Broker の パスを指定 (オプション)                                    |
| BROKER_TOKEN   | Context Broker にアクセスするためのトークンを指定 (オプション)               |
| BROKER_CONTEXT | NGSI タイプが「ld」の時に使用するコンテキストの URL を指定 (オプション)      |


## Docker での実行

本ツール内にある build.sh を実行すると、Docker イメージがビルドされます。

その後、以下のコマンドでツールを実行できます。

### シェルスクリプトでの実行

シェルスクリプト`converter`で実行できます。使用方法で説明した引数と同じものが指定できます。

### dockerコマンドからの実行

以下の docker コマンドを実行できます。

`-e` で始まる部分が設定値(環境変数)です。環境に合わせて変更します。

(例)

```
docker run --rm -it \
-e BROKER_VERSION=v2 \
-e BROKER_URL=http://broker \
-e BROKER_SERVICE=covid19 \
-e BROKER_PATH= \
-e BROKER_TOKEN= \
-e BROKER_CONTEXT= \
fiware-covid19/aggregator \
-m 123456 \
-t CallCenterDaily
```

使用しないオプション値は省略できます。

```
docker run --rm -it \
-e BROKER_URL=http://broker \
-e BROKER_SERVICE=covid19 \
fiware-covid19/aggregator \
-m 123456 \
-t CallCenterDaily
```

## License

Licensed under the [MIT License](../LICENSE).

## Copyright

Copyright (c) 2021 NEC Corporation
