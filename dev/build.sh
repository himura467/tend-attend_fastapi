#!/usr/bin/env bash

set -e

ROOT_DIR=$(cd $(dirname $0)/..; pwd)

source ${ROOT_DIR}/dev/export-requirements.sh
cd ${ROOT_DIR}
docker build -f ${ROOT_DIR}/docker/lambda-server/Dockerfile -t tend-attend --no-cache --provenance=false . --progress=plain
rm ${ROOT_DIR}/requirements.txt
