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
          "cognito-idp:CustomMessage"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:cognito-idp:us-east-1:${data.aws_caller_identity.current.account_id}:userpool/${aws_cognito_user_pool.paradise_cakes_user_pool.id}"
      },
      {
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_attachment" {
  policy_arn = aws_iam_policy.users_api_policy.arn
  role       = aws_iam_role.users_api_role.name
}

resource "aws_iam_role" "cognito_lambda_role" {
  name = "cognito-lambda-role"

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

resource "aws_iam_policy" "cognito_group_policy" {
  name        = "cognito-group-policy"
  description = "Policy to manage Cognito groups"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "cognito-idp:AdminAddUserToGroup"
        ],
        Resource = aws_cognito_user_pool.paradise_cakes_user_pool.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_cognito_attachment" {
  policy_arn = aws_iam_policy.cognito_group_policy.arn
  role       = aws_iam_role.cognito_lambda_role.name
}

