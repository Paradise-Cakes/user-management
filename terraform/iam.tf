resource "aws_iam_role" "cognito_lambda_trigger_role" {
  name = "cognito-trigger-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy" "cognito_trigger_policy" {
  name        = "cognito-trigger-policy"
  description = "Policy to manage Cognito triggers"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "cognito-idp:AdminAddUserToGroup"
        ],
        Resource = aws_cognito_user_pool.paradise_cakes_user_pool.arn
      },
      {
        Effect = "Allow",
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ],
        Resource = aws_cognito_user_pool.paradise_cakes_user_pool.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "cognito_trigger_attachment" {
  policy_arn = aws_iam_policy.cognito_trigger_policy.arn
  role       = aws_iam_role.cognito_lambda_trigger_role.name
}

