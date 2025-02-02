variable "aws_profile" {
  description = "AWS profile"
  type        = string
  default     = "himura"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "domain_name" {
  description = "Domain name"
  type        = string
  default     = "aws.tend-attend.com"
}

variable "common_dbname" {
  description = "Common DB name"
  type        = string
  default     = "tend_attend_common"
}

variable "sequence_dbname" {
  description = "Sequence DB name"
  type        = string
  default     = "tend_attend_sequence"
}

variable "shard_dbname_prefix" {
  description = "Shard DB name prefix"
  type        = string
  default     = "tend_attend_shard"
}

variable "db_shard_count" {
  description = "Number of shards for the DB"
  type        = number
  default     = 2
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "tend-attend-lambda-function"
}

variable "frontend_urls" {
  description = "URLs of the frontend"
  type        = string
  default     = "https://tend-attend.com,https://tend-attend.vercel.app,https://tend-attend-git-release-himura467.vercel.app,https://tend-attend-git-develop-himura467.vercel.app"
}
