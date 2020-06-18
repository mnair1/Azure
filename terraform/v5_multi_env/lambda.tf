resource "aws_lambda_function" "datafence_lambda_function" {
  filename = "lambda_codebase/lambda.zip"
  # function_name = "devops-datafence-lambda-function-automated"
  function_name = "${var.environment}-${var.team}-${var.lambda_name}"
  handler = "lambda_function.lambda_handler"
  #role = "arn:aws:iam::175908995626:role/devops-datafence-lambda-role-automated" # replace account id with your id
  role = "${aws_iam_role.datafence_lambda_role.arn}"
  runtime = "python3.7"
  environment {
    variables = {
      # bucket_name = "devops-datafence-s3-bucket-automated"
      bucket_name = "${aws_s3_bucket.datafence_s3_bucket.id}"
    }
  }
  tags = {
    "Environment" = "${var.environment}"
  }
}