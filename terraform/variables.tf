variable "aws_profile" {
  description = "AWS profile"
  type = string
  default = "himura"
}

variable "aws_region" {
  description = "AWS region"
  type = string
  default = "ap-northeast-1"
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type = string
  default = "tend-attend-lambda-function"
}
