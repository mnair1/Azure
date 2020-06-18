resource "aws_iam_role" "datafence_lambda_role" {
  name = "devops-datafence-lambda-role-automated"

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

resource "aws_iam_role_policy_attachment" "datafence_role_policy_attachment" {
  # depends_on = [aws_iam_role.datafence_lambda_role]
  role       = "${aws_iam_role.datafence_lambda_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
