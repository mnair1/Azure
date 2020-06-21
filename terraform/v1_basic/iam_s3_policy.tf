resource "aws_iam_policy" "datafence_lambda_role_policy" {
  name        = "devops-datafence-s3-put-object-policy"
  path        = "/"
  description = "IAM policy for putting object inside s3"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": ["s3:PutObject"],
      "Resource": "arn:aws:s3:::devops-datafence-s3-bucket-automated/*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "datafence_s3_policy_attachment" {
  depends_on = [aws_iam_role.datafence_lambda_role]
  role       = "devops-datafence-lambda-role-automated"
  policy_arn = aws_iam_policy.datafence_lambda_role_policy.arn
}
