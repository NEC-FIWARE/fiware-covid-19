#!/bin/sh
set -eu
cd $(dirname $0)

: ${1:?変換定義があるディレクトリを指定してください。}

echo "converter"
for file in $(ls -1 "${1%/}/mapping")
do
  echo "${1%/}/mapping/${file}"
  ./converter/converter -m "${1%/}/mapping/${file}"
done

echo "aggregator"
./aggregator/aggregator -c "${1%/}/aggregate_config.yml"
