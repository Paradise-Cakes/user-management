resource "aws_cloudwatch_log_group" "customize_emails_trigger" {
  name              = "/aws/lambda/customize-emails-trigger"
  retention_in_days = var.environment == "prod" ? 7 : 3
}
