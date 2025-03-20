#!/usr/bin/env bash

set -e

ROOT_DIR=$(cd $(dirname $0)/..; pwd)

command=$@

projects=(
  "ta-api"
  "ta-cli"
  "ta-core"
  "ta-ml"
)

for project in "${projects[@]}"; do
  echo "Running ${command} for ${project}"
  cd ${ROOT_DIR}/${project}
  poetry ${command}
done
