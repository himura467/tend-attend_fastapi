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

variable "frontend_url" {
  description = "URL of the frontend"
  type = string
  default = "https://tend-attend.vercel.app"
}

variable "db_shard_count" {
  description = "Number of shards for the DB"
  type = number
  // 現状のデプロイの仕方だと、1以外の値を指定するとエラーになる
  default = 1
}
