data "aws_ecr_repository" "users_api_lambdas" {
  name = var.environment == "prod" ? "users-api-lambdas-us-east-1" : "dev-users-api-lambdas-us-east-1"
}
