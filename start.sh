#!/bin/sh
set -eu
cd $(dirname $0)

: ${1:?変換定義があるディレクトリを指定してください。}

if [ ! -d $1 ]; then
  echo "変換定義があるディレクトリを指定してください。"
  exit 1
fi

docker build -t fiware-covid19/converter ./converter
docker build -t fiware-covid19/aggregator ./aggregator

export CODE=$(sed -n -e '/code:/s/[^0-9]//gp' "${1%/}/aggregate_config.yml")

cd ./docker
docker-compose up -d

until $(curl -s -o /dev/null localhost:1026/version > /dev/null 2>&1); do
  echo "Waiting for FIWARE Orion to be ready."
  sleep 1
done

echo "create index"
docker-compose exec mongo mongo --eval '
 conn = new Mongo();db.createCollection("orion");
 db = conn.getDB("orion");
 db.createCollection("entities");
 db.entities.createIndex({"_id.servicePath": 1, "_id.id": 1, "_id.type": 1}, {unique: true});
 db.entities.createIndex({"_id.type": 1});
 db.entities.createIndex({"_id.id": 1});'
docker-compose exec mongo mongo --eval '
 conn = new Mongo();db.createCollection("orion-covid19");
 db = conn.getDB("orion-covid19");
 db.createCollection("entities");
 db.entities.createIndex({"_id.servicePath": 1, "_id.id": 1, "_id.type": 1}, {unique: true});
 db.entities.createIndex({"_id.type": 1});
 db.entities.createIndex({"_id.id": 1});'

cd -

sleep 3

./get_data.sh $1
