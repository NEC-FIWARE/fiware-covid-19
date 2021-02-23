#!/bin/sh
set -eu
cd $(dirname $0)

METEOROID=./meteoroid
ENDPOINT=$($METEOROID endpoint list | sed -n -e '/converter/p' | sed -e 's/ //g' | awk -F "|" '{print $3}')
curl -X POST "${ENDPOINT}" -H 'Content-Type: application/json' \
-d "{
  \"code\": \"401005\",
  \"broker\": {
    \"url\": \"${ORION_URL}\",
    \"service\": \"covid19\",
    \"path\": \"/\"
  }
}"
