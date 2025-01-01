data "aws_route53_zone" "paradise_cakes" {
  name = var.environment == "prod" ? "megsparadisecakes.com" : "dev.megsparadisecakes.com"
}
