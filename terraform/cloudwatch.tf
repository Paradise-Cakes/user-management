resource "aws_cloudwatch_log_group" "app" {
  name              = "/aws/lambda/users-api-us-east-1"
  retention_in_days = var.environment == "prod" ? 7 : 3
}

resource "aws_cloudwatch_log_group" "customize_emails_trigger" {
  name              = "/aws/lambda/customize-emails-trigger"
  retention_in_days = var.environment == "prod" ? 7 : 3
}
