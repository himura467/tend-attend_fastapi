#!/usr/bin/env bash

SCRIPT_DIR=$(cd $(dirname $0); pwd)
ROOT_DIR=${SCRIPT_DIR}/..

command=$1

projects=(
  "ta-api"
  "ta-core"
  "ta-cli"
)

for project in "${projects[@]}"; do
  echo "Running ${command} for ${project}"
  cd ${ROOT_DIR}/${project}
  poetry run poe ${command}
done
