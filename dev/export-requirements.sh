#!/usr/bin/env bash

set -e

SCRIPT_DIR=$(cd $(dirname $0); pwd)
ROOT_DIR=${SCRIPT_DIR}/..

${SCRIPT_DIR}/poetry-all.sh export -f requirements.txt -o requirements.txt --without-hashes
sort -u ${ROOT_DIR}/*/requirements.txt -o ${ROOT_DIR}/requirements.txt
rm ${ROOT_DIR}/*/requirements.txt
