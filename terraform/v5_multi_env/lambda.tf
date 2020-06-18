resource "aws_lambda_function" "datafence_lambda_function" {
  filename = "lambda_codebase/lambda.zip"
  function_name = "${var.environment}-${var.team}-${var.lambda_name}"
  handler = "lambda_function.lambda_handler"
  role = "${aws_iam_role.datafence_lambda_role.arn}"
  runtime = "python3.7"
  environment {
    variables = {
      bucket_name = "${aws_s3_bucket.datafence_s3_bucket.id}"
    }
  }
  tags = {
    "Environment" = "${var.environment}"
  }
}