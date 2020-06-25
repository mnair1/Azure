resource "aws_iam_role" "datafence_lambda_role" {
  name = "${var.environment}-${var.team}-${var.lambda_role_name}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": "sid"
    }
  ]
}
EOF
}

resource "aws_iam_policy" "datafence_lambda_role_policy" {
  name        = "${var.environment}-${var.team}-${var.s3_policy_name}"
  path        = "/"
  description = "IAM policy for putting object inside s3"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": ["s3:PutObject"],
      "Resource": "${var.s3_bucket_arn}/*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "datafence_role_policy_attachment" {
  role       = aws_iam_role.datafence_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "datafence_s3_policy_attachment" {
  role       = aws_iam_role.datafence_lambda_role.name
  policy_arn = aws_iam_policy.datafence_lambda_role_policy.arn
}
