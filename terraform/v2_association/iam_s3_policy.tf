resource "aws_iam_policy" "datafence_lambda_role_policy_s3" {
  name        = "devops-datafence-s3-put-object-policy"
  path        = "/"
  description = "IAM policy for putting object inside s3"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": ["s3:PutObject"],
      "Resource": "${aws_s3_bucket.datafence_s3_bucket.arn}/*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "datafence_s3_policy_attachment" {
  role       = aws_iam_role.datafence_lambda_role.name
  policy_arn = aws_iam_policy.datafence_lambda_role_policy_s3.arn
}