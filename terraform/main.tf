locals {
  app_name = "tend-attend"
}

terraform {
  required_version = "1.10.2"

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.81.0"
    }
  }
  
  backend "s3" {
    profile = "himura"
    bucket = "tend-attend-terraform-state"
    key = "terraform.tfstate"
    region = "ap-northeast-1"
    acl = "private"
    encrypt = true
    use_lockfile = true
  }
}

provider "aws" {
  profile = var.aws_profile
  region = var.aws_region
}

resource "aws_s3_bucket" "tend_attend_terraform_state" {
  bucket = "tend-attend-terraform-state"
  
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "tend_attend_terraform_state" {
  bucket = aws_s3_bucket.tend_attend_terraform_state.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tend_attend_terraform_state" {
  bucket = aws_s3_bucket.tend_attend_terraform_state.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tend_attend_terraform_state" {
  bucket = aws_s3_bucket.tend_attend_terraform_state.id
  
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

resource "aws_vpc" "tend_attend_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = local.app_name
  }
}

resource "aws_subnet" "tend_attend_subnet_1a" {
  vpc_id = aws_vpc.tend_attend_vpc.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "ap-northeast-1a"
  tags = {
    Name = "${local.app_name}-ap-northeast-1a"
  }
}

resource "aws_subnet" "tend_attend_subnet_1c" {
  vpc_id = aws_vpc.tend_attend_vpc.id
  cidr_block = "10.0.2.0/24"
  availability_zone = "ap-northeast-1c"
  tags = {
    Name = "${local.app_name}-ap-northeast-1c"
  }
}

resource "aws_db_subnet_group" "this" {
  name = "${local.app_name}-db-subnet-group"
  subnet_ids = [
    aws_subnet.tend_attend_subnet_1a.id,
    aws_subnet.tend_attend_subnet_1c.id
  ]
}

resource "aws_security_group" "tend_attend_sg" {
  name = "${local.app_name}-sg"
  vpc_id = aws_vpc.tend_attend_vpc.id

  ingress {
    from_port = 3306
    to_port = 3306
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_rds_cluster_parameter_group" "this" {
  name = "${local.app_name}-cluster-parameter-group"
  family = "aurora-mysql8.0"  # Aurora MySQL 8.4 がリリースされたら変更する

  parameter {
    name = "character_set_server"
    value = "utf8mb4"
  }

  parameter {
    name = "collation_server"
    value = "utf8mb4_general_ci"
  }
}

resource "aws_rds_cluster" "this" {
  cluster_identifier = "${local.app_name}-cluster"
  engine = "aurora-mysql"
  engine_mode = "provisioned"
  engine_version = "8.0.mysql_aurora.3.05.2"
  master_username = "user"
  master_password = "password"
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.this.name
  db_subnet_group_name = aws_db_subnet_group.this.name
  vpc_security_group_ids = [ aws_security_group.tend_attend_sg.id ]

  serverlessv2_scaling_configuration {
    max_capacity = 1.0
    min_capacity = 0.5
  }

  deletion_protection = false
  skip_final_snapshot = true
}

resource "aws_rds_cluster_instance" "this" {
  identifier = "${local.app_name}-instance"
  cluster_identifier = aws_rds_cluster.this.id
  instance_class = "db.serverless"
  engine = aws_rds_cluster.this.engine
  engine_version = aws_rds_cluster.this.engine_version
}

resource "aws_ecr_repository" "tend_attend_repo" {
  name = local.app_name
  force_delete = true
}

resource "terraform_data" "docker_push" {
  triggers_replace = [ timestamp() ]

  provisioner "local-exec" {
    command = <<EOF
      echo "Logging in to Amazon ECR..."
      aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.tend_attend_repo.repository_url}

      echo "Tagging ${local.app_name} image..."
      docker tag ${local.app_name}:latest ${aws_ecr_repository.tend_attend_repo.repository_url}:latest

      echo "Pushing ${local.app_name} image to Amazon ECR..."
      docker push ${aws_ecr_repository.tend_attend_repo.repository_url}:latest
    EOF
  }

  depends_on = [ aws_ecr_repository.tend_attend_repo ]
}

resource "time_sleep" "wait_for_push" {
  depends_on = [ terraform_data.docker_push ]
  create_duration = "30s"
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
        Sid = ""
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_vpc_access_policy" {
  name = "lambda_vpc_access_policy"
  role = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_cloudwatch_policy" {
  role = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "tend_attend_lambda" {
  function_name = var.lambda_function_name
  role = aws_iam_role.lambda_role.arn
  package_type = "Image"
  image_uri = "${aws_ecr_repository.tend_attend_repo.repository_url}:latest"
  architectures = [ "arm64" ]
  depends_on = [ time_sleep.wait_for_push ]
  timeout = 60

  vpc_config {
    subnet_ids = [
      aws_subnet.tend_attend_subnet_1a.id,
      aws_subnet.tend_attend_subnet_1c.id
    ]
    security_group_ids = [ aws_security_group.tend_attend_sg.id ]
  }

  environment {
    variables = {
      AWS_RDS_CLUSTER_INSTANCE_URL = aws_rds_cluster_instance.this.endpoint
      AWS_RDS_CLUSTER_INSTANCE_PORT = aws_rds_cluster_instance.this.port
      AWS_RDS_CLUSTER_MASTER_USERNAME = aws_rds_cluster.this.master_username
      AWS_RDS_CLUSTER_MASTER_PASSWORD = aws_rds_cluster.this.master_password
      AURORA_DATABASE_NAME = "common"
    }
  }
}

resource "aws_api_gateway_rest_api" "tend_attend_api" {
  name = "${local.app_name}-api"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.tend_attend_api.id
  parent_id = aws_api_gateway_rest_api.tend_attend_api.root_resource_id
  path_part = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy_method" {
  rest_api_id = aws_api_gateway_rest_api.tend_attend_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = "ANY"
  authorization = "NONE"
  api_key_required = true
}

resource "aws_lambda_permission" "api_gw" {
  statement_id = "AllowAPIGatewayInvoke"
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tend_attend_lambda.function_name
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.tend_attend_api.execution_arn}/*/*"
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.tend_attend_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_method.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = aws_lambda_function.tend_attend_lambda.invoke_arn
}

resource "aws_api_gateway_deployment" "lambda_deployment" {
  depends_on = [ aws_api_gateway_integration.lambda_integration ]
  rest_api_id = aws_api_gateway_rest_api.tend_attend_api.id
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api-gw/${aws_api_gateway_rest_api.tend_attend_api.name}"
  retention_in_days = 30
}

resource "aws_api_gateway_api_key" "tend_attend_api_key" {
  name = "${local.app_name}-api-key"
}

resource "aws_api_gateway_stage" "dev" {
  deployment_id = aws_api_gateway_deployment.lambda_deployment.id
  rest_api_id = aws_api_gateway_rest_api.tend_attend_api.id
  stage_name = "dev"
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.lambda_deployment.id
  rest_api_id = aws_api_gateway_rest_api.tend_attend_api.id
  stage_name = "prod"
}

resource "aws_api_gateway_usage_plan" "tend_attend_usage_plan" {
  name = "${local.app_name}-usage-plan"
  api_stages {
    api_id = aws_api_gateway_rest_api.tend_attend_api.id
    stage = aws_api_gateway_stage.dev.stage_name
  }
  api_stages {
    api_id = aws_api_gateway_rest_api.tend_attend_api.id
    stage = aws_api_gateway_stage.prod.stage_name
  }
  throttle_settings {
    burst_limit = 5
    rate_limit = 10
  }
  quota_settings {
    limit = 1000
    offset = 0
    period = "MONTH"
  }
}

resource "aws_api_gateway_usage_plan_key" "tend_attend_usage_plan_key" {
  key_id = aws_api_gateway_api_key.tend_attend_api_key.id
  key_type = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.tend_attend_usage_plan.id
}

output "aws_rds_cluster_instance_url" {
  description = "URL of the Amazon RDS cluster instance"
  value = aws_rds_cluster_instance.this.endpoint
}

output "aws_rds_cluster_instance_port" {
  description = "Port of the Amazon RDS cluster instance"
  value = aws_rds_cluster_instance.this.port
}

output "aws_rds_cluster_master_username" {
  description = "Master username of the Amazon RDS cluster"
  value = aws_rds_cluster.this.master_username
}

output "aws_rds_cluster_master_password" {
  description = "Master password of the Amazon RDS cluster"
  value = aws_rds_cluster.this.master_password
  sensitive = true
}

output "aws_ecr_repository_url" {
  description = "URL of the Amazon ECR repository"
  value = aws_ecr_repository.tend_attend_repo.repository_url
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value = aws_lambda_function.tend_attend_lambda.function_name
}

output "api_gateway_invoke_url" {
  description = "Invoke URL of the API Gateway"
  value = aws_api_gateway_deployment.lambda_deployment.invoke_url
}

output "api_gateway_api_key" {
  description = "API key of the API Gateway"
  value = aws_api_gateway_api_key.tend_attend_api_key.value
  sensitive = true
}
