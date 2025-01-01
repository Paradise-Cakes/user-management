data "aws_route53_zone" "users_api" {
  name = var.environment == "prod" ? "users-api.megsparadisecakes.com" : "users-dev-api.megsparadisecakes.com"
}

data "aws_route53_zone" "paradise_cakes" {
  name = var.environment == "prod" ? "megsparadisecakes.com" : "dev.megsparadisecakes.com"
}
