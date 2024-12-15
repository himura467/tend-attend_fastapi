#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(cd $(dirname $0); pwd)
ROOT_DIR=${SCRIPT_DIR}/..

command=$1

projects=(
  "ta-api"
  "ta-cli"
  "ta-core"
)

for project in "${projects[@]}"; do
  echo "Running ${command} for ${project}"
  cd ${ROOT_DIR}/${project}
  poetry run poe ${command}
done
