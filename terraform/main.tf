locals {
  app_name = "tend-attend"
}

terraform {
  required_version = "1.10.2"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.81.0"
    }
  }
  
  backend "s3" {
    profile      = "himura"
    bucket       = "tend-attend-terraform-state"
    key          = "terraform.tfstate"
    region       = "ap-northeast-1"
    acl          = "private"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  profile = var.aws_profile
  region  = var.aws_region
}

resource "aws_route53_zone" "aws_tend_attend_com" {
  name = var.domain_name
}

resource "aws_acm_certificate" "this" {
  domain_name       = var.domain_name
  validation_method = "DNS"
}

resource "aws_route53_record" "this" {
  zone_id  = aws_route53_zone.aws_tend_attend_com.zone_id
  for_each = {
    for dvo in aws_acm_certificate.this.domain_validation_options : dvo.domain_name => {
      name   = dvo.resource_record_name
      type   = dvo.resource_record_type
      record = dvo.resource_record_value
    }
  }
  name     = each.value.name
  type     = each.value.type
  records  = [each.value.record]
  ttl      = 60
}

resource "aws_acm_certificate_validation" "this" {
  certificate_arn         = aws_acm_certificate.this.arn
  validation_record_fqdns = [for record in aws_route53_record.this : record.fqdn]
}

resource "aws_vpc" "tend_attend_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "tend_attend_subnet_1a" {
  vpc_id            = aws_vpc.tend_attend_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "ap-northeast-1a"
}

resource "aws_subnet" "tend_attend_subnet_1c" {
  vpc_id            = aws_vpc.tend_attend_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "ap-northeast-1c"
}

resource "aws_db_subnet_group" "this" {
  name       = "${local.app_name}-db-subnet-group"
  subnet_ids = [
    aws_subnet.tend_attend_subnet_1a.id,
    aws_subnet.tend_attend_subnet_1c.id
  ]
}

resource "aws_security_group" "tend_attend_sg" {
  name   = "${local.app_name}-sg"
  vpc_id = aws_vpc.tend_attend_vpc.id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_secretsmanager_secret" "aurora_credentials" {
  name = "${local.app_name}-aurora-credentials"
}

data "aws_secretsmanager_secret" "data_aurora_credentials" {
  arn = aws_secretsmanager_secret.aurora_credentials.arn
}

resource "random_password" "aurora_master_password" {
  length           = 16
  special          = true
  override_special = "!%&*()-_=+[]{}<>:?"
  min_lower        = 1
  min_numeric      = 1
  min_special      = 1
  min_upper        = 1
}

resource "aws_secretsmanager_secret_version" "aurora_credentials_version" {
  secret_id     = aws_secretsmanager_secret.aurora_credentials.id
  secret_string = jsonencode({
    port     = 3306
    username = "user",
    password = random_password.aurora_master_password.result
  })
}

data "aws_secretsmanager_secret_version" "data_aurora_credentials_version" {
  secret_id = data.aws_secretsmanager_secret.data_aurora_credentials.id
}

locals {
  aurora_credentials = jsondecode(data.aws_secretsmanager_secret_version.data_aurora_credentials_version.secret_string)
}

resource "aws_rds_cluster_parameter_group" "this" {
  name   = "${local.app_name}-cluster-parameter-group"
  family = "aurora-mysql8.0"  # Aurora MySQL 8.4 がリリースされたら変更する

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }

  parameter {
    name  = "collation_server"
    value = "utf8mb4_general_ci"
  }
}

resource "aws_rds_cluster" "this" {
  cluster_identifier              = "${local.app_name}-cluster"
  engine                          = "aurora-mysql"
  engine_mode                     = "provisioned"
  engine_version                  = "8.0.mysql_aurora.3.08.0"
  port                            = local.aurora_credentials.port
  master_username                 = local.aurora_credentials.username
  master_password                 = local.aurora_credentials.password
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.this.name
  db_subnet_group_name            = aws_db_subnet_group.this.name
  vpc_security_group_ids          = [ aws_security_group.tend_attend_sg.id ]
  enable_http_endpoint            = true

  serverlessv2_scaling_configuration {
    max_capacity             = 1.0
    min_capacity             = 0.0
    seconds_until_auto_pause = 300
  }

  deletion_protection = false
  skip_final_snapshot = true

  depends_on = [ aws_secretsmanager_secret_version.aurora_credentials_version ]
}

resource "aws_rds_cluster_instance" "this" {
  identifier         = "${local.app_name}-instance"
  cluster_identifier = aws_rds_cluster.this.id
  instance_class     = "db.serverless"
  engine             = aws_rds_cluster.this.engine
  engine_version     = aws_rds_cluster.this.engine_version
}

resource "aws_iam_role" "lambda_role" {
  name               = "lambda_role"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect    = "Allow"
        Sid       = ""
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_vpc_access_policy" {
  name   = "lambda_vpc_access_policy"
  role   = aws_iam_role.lambda_role.id
  policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action   = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_cloudwatch_policy" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "tend_attend_lambda" {
  function_name    = var.lambda_function_name
  role             = aws_iam_role.lambda_role.arn
  filename         = "../app.zip"
  source_code_hash = filebase64sha256("../app.zip")
  handler          = "main.lambda_handler"
  runtime          = "python3.10"
  timeout          = 60
  memory_size      = 2048

  vpc_config {
    subnet_ids         = [
      aws_subnet.tend_attend_subnet_1a.id,
      aws_subnet.tend_attend_subnet_1c.id
    ]
    security_group_ids = [ aws_security_group.tend_attend_sg.id ]
  }

  environment {
    variables = {
      FRONTEND_URLS                   = var.frontend_urls
      COOKIE_DOMAIN                   = var.cookie_domain
      JWT_SECRET_KEY                  = var.jwt_secret_key
      AWS_SECRETSMANAGER_SECRET_ID    = aws_secretsmanager_secret.aurora_credentials.id
      AWS_SECRETSMANAGER_REGION       = var.aws_region
      DB_SHARD_COUNT                  = var.db_shard_count
      AWS_RDS_CLUSTER_INSTANCE_URL    = aws_rds_cluster_instance.this.endpoint
      AWS_RDS_CLUSTER_INSTANCE_PORT   = local.aurora_credentials.port
      AWS_RDS_CLUSTER_MASTER_USERNAME = local.aurora_credentials.username
      AWS_RDS_CLUSTER_MASTER_PASSWORD = local.aurora_credentials.password
      AURORA_COMMON_DBNAME            = var.common_dbname
      AURORA_SEQUENCE_DBNAME          = var.sequence_dbname
      AURORA_SHARD_DBNAME_PREFIX      = var.shard_dbname_prefix
      CHECKPOINT_PATH                 = var.checkpoint_path
    }
  }
}

resource "aws_api_gateway_rest_api" "tend_attend_api" {
  name = "${local.app_name}-api"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.tend_attend_api.id
  parent_id   = aws_api_gateway_rest_api.tend_attend_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tend_attend_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.tend_attend_api.execution_arn}/*/*"
}

resource "aws_api_gateway_method" "proxy_method" {
  rest_api_id      = aws_api_gateway_rest_api.tend_attend_api.id
  resource_id      = aws_api_gateway_resource.proxy.id
  http_method      = "ANY"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.tend_attend_api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.tend_attend_lambda.invoke_arn
  timeout_milliseconds    = 60000
}

resource "aws_api_gateway_method" "proxy_options" {
  rest_api_id   = aws_api_gateway_rest_api.tend_attend_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "proxy_options" {
  rest_api_id             = aws_api_gateway_rest_api.tend_attend_api.id
  resource_id             = aws_api_gateway_resource.proxy.id
  http_method             = aws_api_gateway_method.proxy_options.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.tend_attend_lambda.invoke_arn
}

resource "aws_api_gateway_deployment" "lambda_deployment" {
  depends_on  = [ aws_api_gateway_integration.lambda_integration, aws_api_gateway_integration.proxy_options ]
  rest_api_id = aws_api_gateway_rest_api.tend_attend_api.id
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name              = "/aws/api-gw/${aws_api_gateway_rest_api.tend_attend_api.name}"
  retention_in_days = 30
}

resource "aws_api_gateway_api_key" "tend_attend_api_key" {
  name = "${local.app_name}-api-key"
}

resource "aws_api_gateway_stage" "dev" {
  deployment_id = aws_api_gateway_deployment.lambda_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.tend_attend_api.id
  stage_name    = "dev"
}

resource "aws_api_gateway_stage" "prod" {
  deployment_id = aws_api_gateway_deployment.lambda_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.tend_attend_api.id
  stage_name    = "prod"
}

resource "aws_api_gateway_domain_name" "tend_attend_domain_name" {
  domain_name              = var.domain_name
  regional_certificate_arn = aws_acm_certificate.this.arn

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_base_path_mapping" "prod_mapping" {
  domain_name = aws_api_gateway_domain_name.tend_attend_domain_name.domain_name
  api_id      = aws_api_gateway_rest_api.tend_attend_api.id
  stage_name  = aws_api_gateway_stage.prod.stage_name
}

resource "aws_api_gateway_usage_plan" "tend_attend_usage_plan" {
  name = "${local.app_name}-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.tend_attend_api.id
    stage  = aws_api_gateway_stage.dev.stage_name
  }
  api_stages {
    api_id = aws_api_gateway_rest_api.tend_attend_api.id
    stage  = aws_api_gateway_stage.prod.stage_name
  }

  throttle_settings {
    burst_limit = 5
    rate_limit  = 10
  }
  quota_settings {
    limit  = 1000
    offset = 0
    period = "DAY"
  }
}

resource "aws_api_gateway_usage_plan_key" "tend_attend_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.tend_attend_api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.tend_attend_usage_plan.id
}

resource "aws_route53_record" "api_gw" {
  name    = aws_api_gateway_domain_name.tend_attend_domain_name.domain_name
  zone_id = aws_route53_zone.aws_tend_attend_com.zone_id
  type    = "A"
  alias {
    name                   = aws_api_gateway_domain_name.tend_attend_domain_name.regional_domain_name
    zone_id                = aws_api_gateway_domain_name.tend_attend_domain_name.regional_zone_id
    evaluate_target_health = true
  }  
}

output "aws_rds_cluster_instance_url" {
  description = "URL of the Amazon RDS cluster instance"
  value       = aws_rds_cluster_instance.this.endpoint
}

output "aws_rds_cluster_instance_port" {
  description = "Port of the Amazon RDS cluster instance"
  value       = local.aurora_credentials.port
  sensitive   = true
}

output "aws_rds_cluster_master_username" {
  description = "Master username of the Amazon RDS cluster"
  value       = local.aurora_credentials.username
  sensitive   = true
}

output "aws_rds_cluster_master_password" {
  description = "Master password of the Amazon RDS cluster"
  value       = local.aurora_credentials.password
  sensitive   = true
}

output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = aws_lambda_function.tend_attend_lambda.function_name
}

output "api_gateway_invoke_url" {
  description = "Invoke URL of the API Gateway"
  value       = aws_api_gateway_deployment.lambda_deployment.invoke_url
}

output "api_gateway_api_key" {
  description = "API key of the API Gateway"
  value       = aws_api_gateway_api_key.tend_attend_api_key.value
  sensitive   = true
}
