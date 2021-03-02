#!/bin/sh
set -eu
cd $(dirname $0)

cd openwhisk-devtools/docker-compose/
DOCKER_IMAGE_TAG=1.0.0 make stop
cd -

cd fiware-meteoroid/docker/
docker-compose down
