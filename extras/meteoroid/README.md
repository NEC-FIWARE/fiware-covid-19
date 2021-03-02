# FIWARE Covid-19 Meteoroid

FIWARE [Meteoroid](https://github.com/OkinawaOpenLaboratory/fiware-meteoroid) は、FIWARE から通知されたイベントによって、ビジネスロジック (ファンクション) を実行できるオープンソースソフトウェアです。[Okinawa Open Laboratory](https://github.com/OkinawaOpenLaboratory) によって開発されています。
FIWARE Covid-19 の変換ツール、および、集計ツールをファンクション化することで、外部イベントをトリガーにして、変換・集計処理を実行できます。

## Meteoroid 環境の構築

[Meteoroid - getting started](https://fiware-meteoroid.readthedocs.io/en/latest/getting_started/) のドキュメントにしたがって、Meteoroid と Orion が稼働する環境を構築していください。また、MongoDB に適切なインデックスを作成してください。

## リポジトリのクローン

git コマンドを使用してリポジトリをクローンします。

```
git clone https://github.com/NEC-FIWARE/fiware-covid-19.git
cd fiware-covid-19/extras/meteoroid
```

## 環境変数の設定

Meteoroid-Core と Orion のコンテナが動作しているホスト OS の IP アドレスを使用して、以下の２つの環境変数を設定してください。`192.168.0.1` を環境に合わせて変更してください。

```
export METEOROID_SCHEMA_ENDPOINT=http://192.168.0.1:3000/schema/?format=corejson
export ORION_URL=http://192.168.0.1:1026
```

## Meteoroid-cli のビルド

Meteoroid-cli のコンテナイメージをビルドします。`./meteoroid` でコマンドを実行できるようになります。

```
./build_meteoroid-cli.sh
```

## ファンクションとエンドポイントの登録

ファンクションとエンドポイントを登録します。

```
./add_functions.sh
```

登録されたファンクションを確認します。

```console
./meteoroid function list
```

```console
+----+------+----------+--------+------+---------+------------+----------------+---------------------+------------+
| id | code | language | binary | main | version | parameters | fiware_service | fiware_service_path | name       |
+----+------+----------+--------+------+---------+------------+----------------+---------------------+------------+
|  1 |      | python:3 | False  |      | 0.0.1   |            |                | /                   | Converter  |
|  2 |      | python:3 | False  |      | 0.0.1   |            |                | /                   | Aggregator |
+----+------+----------+--------+------+---------+------------+----------------+---------------------+------------+
```

登録されたエンドポイントを確認します。

```console
./meteoroid endpoint list
```

```console
+----+-------------------------------------------------------------------------------------+----------------+---------------------+---------+-------------+--------+----------+
| id | url                                                                                 | fiware_service | fiware_service_path | name    | path        | method | function |
+----+-------------------------------------------------------------------------------------+----------------+---------------------+---------+-------------+--------+----------+
|  1 | http://192.168.0.1:9090/api/23bc46b1-71f6-4ed5-8c54-816aa4f8c502/covid19/converter  |                | /                   | covid19 | /converter  | post   |        1 |
|  2 | http://192.168.0.1:9090/api/23bc46b1-71f6-4ed5-8c54-816aa4f8c502/covid19/aggregator |                | /                   | covid19 | /aggregator | post   |        2 |
+----+-------------------------------------------------------------------------------------+----------------+---------------------+---------+-------------+--------+----------+
```

## サブスクリプションの登録

変換ファンクションと集計ファンクションを連携させるためのサブスクリプションを登録します。サブスクリプションの通知先は、集計ファンクションのエンドポイントです。

```console
./subscription.sh
```

登録したサブスクリプションは以下のコマンドで確認できます。

```
curl $ORION_URL/v2/subscriptions -H 'Fiware-Service: covid19' -H 'Fiware-ServicePath: /'
```

## 変換定義と集計定義の登録

Orion に変換定義と集計定義を登録します。

```console
./upload.sh example/401005_kitakyushu/
```

変換定義と集計定義のエンティティが登録されたことを確認できます。

```console
curl $ORION_URL/v2/types?options=values -H 'Fiware-Service: covid19' -H 'Fiware-ServicePath: /'
```

```console
["Covid19Aggregate","Covid19Mapping"]
```

## 処理のトリガー

変換ファンクションのエンドポイントにリクエストを送信して、一連の処理を実行します。

```console
./invoke.sh
```

処理が完了すると、集計結果のエンティティが作成されます。

```console
curl $ORION_URL/v2/types?options=values -H 'Fiware-Service: covid19' -H 'Fiware-ServicePath: /'
```

```console
["Covid19Aggregate","Covid19CallCenter","Covid19CallCenterDailyAggregated","Covid19ConfirmNegative","Covid19ConfirmNegativeDailyAggregated","Covid19Mapping","Covid19Patients","Covid19PatientsDailyAggregated","Covid19PatientsListAggregated","Covid19PatientsSummary","Covid19Status","Covid19TestCount","Covid19TestCountDailyAggregated","Covid19TestPeopleDailyAggregated"]
```

## Copyright

Copyright (c) 2021 NEC Corporation
