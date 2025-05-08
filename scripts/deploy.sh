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
# image の tag を latest に固定しているため、一度 destroy しないと更新されない
terraform destroy -target=aws_lambda_function.tend_attend_lambda
terraform apply
