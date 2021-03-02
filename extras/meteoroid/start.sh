#!/bin/sh
set -eu
cd $(dirname $0)

# setup OpneWhisk
if [ ! -d openwhisk-devtools ] ; then
  git clone https://github.com/apache/openwhisk-devtools.git
fi
cd openwhisk-devtools/docker-compose/
DOCKER_IMAGE_TAG=1.0.0 make quick-start
cd -

# setup FIWARE Orion and Meteoroid
if [ ! -d fiware-meteoroid ] ; then
  git clone https://github.com/OkinawaOpenLaboratory/fiware-meteoroid.git
fi
cd fiware-meteoroid/docker/
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

# setup meteoroid-cli
docker build -t fiware-covid19/meteoroid-cli ./meteoroid-cli
