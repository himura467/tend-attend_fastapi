#!/usr/bin/env bash

set -e

ROOT_DIR=$(cd $(dirname $0)/..; pwd)

projects=(
  "ta-api"
  "ta-core"
  "ta-ml"
)

for project in "${projects[@]}"; do
  echo "Running export for ${project}"
  cd ${ROOT_DIR}/${project}
  poetry export -f requirements.txt -o requirements.txt --without-hashes
done

grep -hv "tend-attend" ${ROOT_DIR}/*/requirements.txt | sort -u -o ${ROOT_DIR}/requirements.txt
rm ${ROOT_DIR}/*/requirements.txt
