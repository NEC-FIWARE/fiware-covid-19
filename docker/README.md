# Web サイト

FIWARE Covid-19 の Web サイトを起動するためには、covid19, orion, mongo, nginx の Docker コンテナが必要です。Docker Compose を使用して、この一連の Docker コンテナのビルド、取得、起動、停止を行います。covid19のソースコードは、Tokyo Metropolitan Government がオープンソースとして公開している「[東京都 新型コロナウイルス感染症対策サイト](https://github.com/tokyo-metropolitan-gov/covid19) 」の派生物で、オリジナルのソースコードに、FIWARE対応の機能を追加したものです。

## docker-compose.yml の例

Docker Comopse を使用するには、docker-compose.yml が必要です。その例は以下の通りです。

```yaml
version: "3"
services:

  covid19:
    container_name: covid19
    build:
      context: ./
      dockerfile: ./Dockerfile
    image: fiware-covid19/covid19
    tty: true
    environment:
      - NUXT_ENV_MUNICIPALITY_CODE=$CODE
      - NUXT_ENV_BROKER_SERVICE=covid19
      - NUXT_ENV_BROKER_PATH=/
    volumes:
      - node_modules:/app/node_modules

  orion:
    container_name: orion
    image: fiware/orion:2.5.2
    depends_on:
      - mongo
    ports:
      - "1026:1026"
    command: -dbhost mongo

  mongo:
    container_name: mongo
    image: mongo:3.6
    command: --nojournal
    volumes:
      - ./data/v2/db:/data/db
      - ./data/v2/conf:/data/configdb

  nginx:
    container_name: nginx
    image: nginx
    ports:
      - "3000:80"
    depends_on:
      - covid19
      - orion
    volumes:
      - ./v2.conf:/etc/nginx/conf.d/default.conf:ro

volumes:
  node_modules: {}
```

orion, mongo, nginx のコンテナは、ビルド済みのイメージを、Docker Hub から取得します。cvoid19 のコンテナ イメージは、Dockerfile を使ってビルドします。covid19 のソースコードは、[こちら](https://github.com/NEC-FIWARE/covid19)から取得します。

### 環境変数の設定

docker-compose.yml 内の covid19 コンテナの環境変数を、利用環境に合わせて編集します。

| 環境変数                   | 説明                                                      |
| -------------------------- | --------------------------------------------------------- |
| NUXT_ENV_MUNICIPALITY_CODE | 地方公共団体コードを指定 (必須)                           |
| NUXT_ENV_BROKER_SERVICE    | Context Broker の サービス (テナント) を指定 (オプション) |
| NUXT_ENV_BROKER_PATH       | Context Broker の パスを指定 (NGSI v2 のみのオプション)   |

docker-compose.yml は初期設定済みの構成なので、特に必要のある場合以外は変更する必要はありません。

### 起動

リポジトリのルートディレクトリにあるシェルスクリプト `start.sh` を起動することで Web サイトが起動します。
これは 一連の Docker コンテナ イメージのビルドとオープンデータの取り込み、Weｂ サイト起動を一括で行います。
詳細は[こちら](../README.md)の「利用方法」を参照ください。

## Copyright

Copyright (c) 2021 NEC Corporation
