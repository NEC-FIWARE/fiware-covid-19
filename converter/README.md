# 変換ツール

本変換ツールは、csv ファイルや json ファイルの変換元データ (以下、元データと記載) を NGSI 形式のデータに変換して、Context Broker に保存する CLI ツールです。自治体が公開する Covid-19 対策に関するオープンデータを対象とし、Code for Japan が公開している[新型コロナウイルス感染症対策に関するオープンデータ項目定義書](https://www.code4japan.org/activity/stopcovid19#doc)の項目を共通データモデルとして利用して、NGSI 形式のデータに変換します。

## 使用方法

変換ツールには、"元データ"、"保存先情報”、"変換定義"を指定します。

```console
./converter.py --help
usage: converter.py [-h] [-m MAP] [-f FILE] [-j] [-s] [--dryrun] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  -m MAP, --map MAP     mapping file
  -f FILE, --file FILE  covid-19 file
  -j, --json            file type json
  -s, --sjis            shift_jis encording
  --dryrun              dryrun
  --debug               debug
```

| 項目       | 説明                                          |
| ---------- | --------------------------------------------- |
| -h, --help | コマンドのヘルプを表示                        |
| -m, --map  | 変換定義ファイルを指定 (必須)                 |
| -f, --file | 元データのファイルを指定                      |
| -j, --json | 元データを json として処理                    |
| -s, --sjis | 元データの文字コードをSJISとして処理          |
| --dryrun   | Context Broker への保存処理の直前で実行を中止 |
| --debug    | Context Broker へのクエリを標準出力に出力     |

## 動作環境

変換ツールは python3 で記述されいます。python3i が導入された環境で利用できます。また、yml ファイルを読み込むために、`pyyaml` を使用します。事前にインストールしてくさい。

```console
cd converter/
pip install -r requirements.txt
```

## Docker での実行

Docker が利用できる環境の場合、converter.py のコンテナイメージを利用できます。この場合、`python3` や `pyymal` のインストールは不要です。

### コンテナイメージのビルド

シェルスクリプトの `build.sh` を実行すると、コンテナイメージ `fiware-covid19/converter` が作成されます。

```console
./build.sh
```

### コンテナイメージの実行

シェルスクリプト`converter` で実行できます。使用方法で説明した引数と同じものが指定できます。

```console
./converter
```

## 元データ

Covid-19 対策関連データが保存された入力ファイルです。

### ファイル要件

- 対象データ: 新型コロナウィルス感染症対策オープンデータ
  - 陽性患者属性
  - 検査実施人数
  - 検査実施件数
  - 陰性確認数
  - コールセンター相談件数
- 必須データ項目: Code for Japan が公開している[新型コロナウイルス感染症対策に関するオープンデータ項目定義書](https://www.code4japan.org/activity/stopcovid19#doc)で定義されている必須項目および全国地方公共団体コード
- データ形式: csv または json
- csv の要件
  - 先頭1行目がデータ項目が記述されたヘッダ行であること。先頭行が空白だったり、ヘッダが2行以降にならないこと
  - csv 末尾に余計な空行、コメント等が入らないこと
  - 先頭1行目がデータ項目数と以降の各行のデータ数が一致していること
- 文字コード: UTF-8 または Shift JIS 

### 指定方法

元データは変換ツールの入力データで、次の方法で指定できます。

- コマンドの引数 (-f, --file) でファイル名を指定
- 変換定義内で指定
- 標準入力

## 保存先情報

変換したデータは、Context Broker に NGSI 形式のデータとして保存されます。保存先情報は、次の方法で指定できます。両方の指定がある場合、変換定義内の指定が使用されます。

- `conv.py` と同じディレクトリに `conv.yml` という名前のファイルを作成して保存先情報を指定
- 変換定義内で指定

保存先情報は yml 形式で記述し、項目は次の通りです。

### version

変換定義のバージョンを指定します。"1" を設定してください。

### broker

| 項目名  | 説明                                                                                           |
| ------- | ---------------------------------------------------------------------------------------------- |
| url     | Context Broker の URL (必須)                                                                   |
| type    | NGSI のタイプ。`v2` または `ld`。指定がない場合は`v2`                                          |
| serivce | FIWARE-Service                                                                                 |
| path    | FIWARE-ServicePath (Orion の場合のみ有効)                                                      |
| token   | OAuth2 トークン。文字列または環境変数で指定                                                    |
| context | @context の URL (Orion-LD の場合のみ必要)                                                      |
| limit   | Context Broker へのクエリに含めるエンティティ数。既定値: 1,000。指定可能な範囲：1以上3,000以下 |

### ymlサンプル

```console
version: "1"

broker:
  url: "http://localhost:1026"
  service: "covid19"
  path: "/test"
```

## 変換定義

変換定義とは元データの項目と NGSI インフォメーョンモデルの属性との関係の定義です。
変換定義は yaml ファイルに記述します。変換定義に加えて、元データのメタデータ情報、元データのファイルに関する情報、保存先情報を定義できます。記述項目は次の通りです。

### version (必須)

変換定義ファイルバージョンを指定します。"1"を設定してください。

### metadata (オプション)

元データのメタデータを指定します。アプリケーションはこれらの項目を使用しません。

| 項目名      | 説明                          |
| ----------- | ----------------------------- |
| title       | データのタイトル              |
| description | データの説明                  |
| source      | オープンデータサイトのURL     |
| author      | 作成者                        |
| licnse      | ライセンス                    |
| remarks     | 備考                          |

### source (オプション)

元データのファイルに関する情報を指定します。

| 項目名   | 説明                                                                   |
| -------- | ---------------------------------------------------------------------- |
| file     | データのパスまたは URL                                                 |
| encoding | 文字コード。`utf_8_sig` または`shift_jis`。指定がない場合は`utf_8_sig` |
| type     | ファイルのタイプ。`csv`または`json`。指定がない場合は`csv`             |
| apikey   | 文字列または環境変数で指定                                             |

#### 設定例

ローカルにあるファイルを元データとして指定します。

```console
source:
  file: 401307_city_fukuoka_covid19_patients.csv
```

オープンデータ API を使用して元データを取得します。環境変数 `NGSI_CONV_APIKEY` の値を apikey として使用します。

```console
source:
  file: "https://api.opendata.go.jp/tokyo-to/call-center-cases"
  type: json
  apikey: "NGSI_CONV_APIKEY"
```

### broker (オプション)

Context Broker に関連する保存先情報を定義します。

| 項目名  | 説明                                                                                           |
| ------- | ---------------------------------------------------------------------------------------------- |
| url     | Context Broker の URL (必須)                                                                   |
| type    | NGSI のタイプ。`v2` または `ld`。指定がない場合は`v2`                                          |
| serivce | FIWARE-Service                                                                                 |
| path    | FIWARE-ServicePath (Orion の場合のみ有効)                                                      |
| token   | OAuth2 トークン。文字列または環境変数で指定                                                    |
| context | @context の URL (Orion-LD の場合のみ必要)                                                      |
| limit   | Context Broker へのクエリに含めるエンティティ数。既定値: 1,000。指定可能な範囲：1以上3,000以下 |

### mapping (必須)

元データとのマッピングを定義します。サブ項目の attributes に対応関係を記述します。

#### attributes (必須)

元データの項目名と NGSI 属性型との対応関係を定義します。

| 項目名  | 説明                                                                          |
| ------- | ----------------------------------------------------------------------------- |
| name    | NGSI 属性名としてデータモデル定義の項目名 または独自定義の項目名を指定 (必須) |
| key     | CSV 項目名または JSON のキー名(第一階層)                                      |
| default | デフォルト値の指定。数値、文字列                                              |
| serial  | データ毎に連続した一意の数値を生成。開始番号。既定値1                         |
| format  | (日付の場合)元データの日付フォーマット                                        |
| type    | NGSI 属性型 Number, Text, DateTime                                            |

#### id (オプション)

| 項目名 | 説明                                                                                  |
| ------ | ------------------------------------------------------------------------------------- |
| id     | NGSI エンティティ ID の末尾に追加する一意の数値。数値または一意の数値を持つNGSI属性名 |

## 変換定義例

次のような YAML ファイルに定義を記述します。

```
version: "1"

metadata:
  title: "福岡市 新型コロナウイルス感染症 陽性患者発表情報"
  source: "https://ckan.open-governmentdata.org/dataset/401307_covid19_patients"
  author: "福岡市"
  license: "CC-BY"

source:
  file: "https://~~~~/xxx.csv"
  encoding: "Shift_JIS"
  type: csv
  apikey: xxxxxxxx

broker:
  type: "v2"
  url: "http://localhost:1026"
  service: "covid19"
  path: "/fukuoka"

mapping:
  attributes:
    - name: patientNo
      key: "No"

    - name: municipalityCode
      key: "全国地方公共団体コード"
      default: "4000001"

    - name: prefectureName
      key: "都道府県名"

    - name: cityName
      key: "市区町村名"

    - name: publishedAt
      key: "公表_年月日"
      format: "%Y/%m/%d"

    - name: symptomOnsetAt
      key: "発症_年月日"
      format: "%Y/%m/%d"

    - name: patientResidence
      key: "居住地"

    - name: patientAge
      key: "年代"

    - name: patientGender
      key: "性別"

    - name: patientOccupation
      key: "患者_属性"

    - name: patientCondition
      key: "患者_状態"

    - name: patientSymptoms
      key: "患者_症状"

    - name: patientTravelHistory
      key: "患者_渡航歴の有無フラグ"

    - name: patientDischarged
      key: "退院済フラグ"

    - name: remarks
      key: "備考"

    - name: weeekday
      key: "曜日"
      type: "Text"
```

### 日付項目の設定例

元データの日付の形式を次のような定義で指定できます。日付フォーマット `format` には、Python3 の日付型を使用できます。仕様の詳細は、「[datetime --- 基本的な日付型および時間型](https://docs.python.org/ja/3/library/datetime.html)」を参照ください。

```
    - name: symptomOnsetAt
      key: "発症_年月日"
      format: "%Y/%m/%d" 
```

### デフォルト値の設定例

元データに対応する項目名はあるがデータが空の場合、次のように固定値を設定できます。

```
    - name: municipalityCode
      key: "全国地方公共団体コード"
      default: "130001"
```

元データに「全国地方公共団体コード」の項目がない場合に、次のような定義で固定値を設定できます。

```
    - name: municipalityCode
      default: "130001"
```

元データに項番や通し番号等がない場合、次のような定義で一意の番号を設定できます。

```
    - name: patientNo
      serial: 1000
```

### 独自項目の追加例

次のような定義で Covid-19 データモデルに独自項目を追加できます。type には、数値の場合は `Number` を、文字列の場合は `Text` を、日付の場合は `DateTime` を指定します。

```
    - name: weeekday
      key: "曜日"
      type: "Text"
```

```
    - name: modifiedAt
      key: "更新日"
      type: "DateTime"
      format: "%Y/%m/%d" 
```

### idの設定例

1,000からの連番を id に付加

```console
mapping:
  id: 1000
```

patientNo の値を id に付加

```console
mapping:
  id: patientNo
```

## License

Licensed under the [MIT License](../LICENSE).

## Copyright

Copyright (c) 2021 NEC Corporation
