#!/bin/sh
set -eu
cd $(dirname $0)

METEOROID=./meteoroid

# Create functions
$METEOROID function create Converter function/converter.py --language python:3
CONV=$($METEOROID function list | sed -n -e '/Converter/p' | sed -e 's/ //g' | awk -F "|" '{print $2}')
$METEOROID function create Aggregator function/aggregator.py --language python:3
AGGR=$($METEOROID function list | sed -n -e '/Aggregator/p' | sed -e 's/ //g' | awk -F "|" '{print $2}')

# Create endpoints
$METEOROID endpoint create covid19 /converter post $CONV
$METEOROID endpoint create covid19 /aggregator post $AGGR

echo "function"
$METEOROID function list
echo "endpoint"
$METEOROID endpoint list
