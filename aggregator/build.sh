#!/bin/sh
set -eu
cd $(dirname $0)

docker build . -t fiware-covid19/aggregator
