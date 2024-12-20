locals {
  lambda_image = "${data.aws_ecr_repository.users_api_lambdas.repository_url}:${var.docker_image_tag}"
}

resource "aws_lambda_function" "app" {
  image_uri     = local.lambda_image
  package_type  = "Image"
  function_name = var.environment == "prod" ? "users-api-us-east-1" : "dev-users-api-us-east-1"
  role          = aws_iam_role.users_api_role.arn

  timeout     = 30
  memory_size = 1024

  image_config {
    command = ["src.api.lambda_handler"]
  }

  environment {
    variables = {
      REGION = "us-east-1"
    }
  }
}


