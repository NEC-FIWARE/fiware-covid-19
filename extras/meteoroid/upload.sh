#!/bin/sh
set -eu
cd $(dirname $0)

: ${1:?変換定義があるディレクトリを指定してください。}

if [ ! -d $1 ]; then
  echo "変換定義があるディレクトリを指定してください。"
  exit 1
fi

for file in ${1%/}/*.json
do
  echo @$file
  curl -X POST "${ORION_URL%/}/v2/entities?options=keyValues,upsert" \
  -H "Content-Type: application/json"  -H "Fiware-Service: covid19" -H "Fiware-ServicePath: /" \
  --data @$file
done
