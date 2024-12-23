resource "aws_iam_role" "users_api_role" {
  name = "users-api-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy" "users_api_policy" {
  name        = "users-api-policy"
  description = "users api policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "execute-api:Invoke"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:execute-api:us-east-1:${data.aws_caller_identity.current.account_id}:*/*/*/*"
      },
      {
        Action   = "lambda:InvokeFunction",
        Effect   = "Allow",
        Resource = aws_lambda_function.app.arn
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:PostLogEvents",
        ],
        Effect   = "Allow",
        Resource = "*"
      },
      {
        Action   = "dynamodb:Query",
        Effect   = "Allow",
        Resource = "arn:aws:dynamodb:us-east-1:${data.aws_caller_identity.current.account_id}:table/users/index/order-type-index"
      },
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:UpdateItem",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:BatchWriteItem",
          "dynamodb:BatchGetItem",
        ]
        Effect   = "Allow",
        Resource = "arn:aws:dynamodb:us-east-1:${data.aws_caller_identity.current.account_id}:table/*"
      },
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject",
        ]
        Effect = "Allow",
        Resource = [
          "arn:aws:s3:::desserts-images",
          "arn:aws:s3:::desserts-images/*"
        ]
      },
      {
        Action = [
          "cognito-idp:AdminAddUserToGroup",
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_attachment" {
  policy_arn = aws_iam_policy.users_api_policy.arn
  role       = aws_iam_role.users_api_role.name
}
