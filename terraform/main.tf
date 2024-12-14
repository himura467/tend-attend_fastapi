locals {
  app_name = "tend-attend"
}

provider "aws" {
  region = var.aws_region
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
      sleep 10  # Wait for the image to be available
    EOF
  }

  depends_on = [ aws_ecr_repository.tend_attend_repo ]
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

resource "aws_iam_role_policy_attachment" "lambda_attachment" {
  role = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "tend_attend_lambda" {
  function_name = var.lambda_function_name
  role = aws_iam_role.lambda_role.arn
  package_type = "Image"
  image_uri = "${aws_ecr_repository.tend_attend_repo.repository_url}:latest"
  depends_on = [ terraform_data.docker_push ]
}

resource "aws_api_gateway_rest_api" "tend_attend_api" {
  name = "tend-attend-api"
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
  name = "tend-attend-api-key"
}

resource "aws_api_gateway_usage_plan" "tend_attend_usage_plan" {
  name = "tend-attend-usage-plan"
  api_stages {
    api_id = aws_api_gateway_rest_api.tend_attend_api.id
    stage = aws_api_gateway_deployment.lambda_deployment.stage_name
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