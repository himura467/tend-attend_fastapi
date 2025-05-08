#!/usr/bin/env bash

set -e

ROOT_DIR=$(cd $(dirname $0)/..; pwd)

bash ${ROOT_DIR}/dev/export-requirements.sh
docker build -f ${ROOT_DIR}/docker/lambda-server/Dockerfile -t tend-attend --no-cache --provenance=false . --progress=plain
rm ${ROOT_DIR}/requirements.txt
