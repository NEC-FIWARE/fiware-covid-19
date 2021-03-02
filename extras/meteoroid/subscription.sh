#!/bin/sh
set -eu
cd $(dirname $0)

METEOROID=./meteoroid
ENDPOINT=$($METEOROID endpoint list | sed -n -e '/aggregator/p' | sed -e 's/ //g' | awk -F "|" '{print $2}')

$METEOROID subscription create --fiwareservice covid19 --fiwareservicepath / ${ENDPOINT} '{
  "description": "FIWARE Covid19 aggregator",
  "subject": {
    "entities": [
      {
        "idPattern": ".*",
        "type": "Covid19Aggregate"
      }
    ]
  },
  "notification": {
    "attrsFormat": "keyValues"
  }
}'
