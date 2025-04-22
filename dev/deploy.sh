#!/usr/bin/env bash

set -e

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <aws-profile>"
  exit 1
fi

export AWS_PROFILE=$1

ROOT_DIR=$(cd $(dirname $0)/..; pwd)

cd $ROOT_DIR/terraform

terraform init
terraform apply
