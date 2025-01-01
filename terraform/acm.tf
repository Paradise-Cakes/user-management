data "aws_acm_certificate" "users_api" {
  domain      = var.environment == "prod" ? "users-api.megsparadisecakes.com" : "users-dev-api.megsparadisecakes.com"
  types       = ["AMAZON_ISSUED"]
  most_recent = true
}
