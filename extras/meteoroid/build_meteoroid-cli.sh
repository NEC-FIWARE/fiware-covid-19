#!/bin/sh
set -eu
cd $(dirname $0)

# setup meteoroid-cli
docker build -t fiware-covid19/meteoroid-cli ./meteoroid-cli
