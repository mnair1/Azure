resource "aws_lambda_function" "datafence_lambda_function" {
  filename = "lambda_codebase/lambda.zip"
  function_name = "devops-datafence-lambda-function-automated"
  handler = "lambda_function.lambda_handler"
  role = "arn:aws:iam::175908995626:role/devops-datafence-lambda-role-automated" # replace account id with your id
  runtime = "python3.7"
  environment {
    variables = {
      bucket_name = "devops-datafence-s3-bucket-automated"
    }
  }
  tags = {
    "Environment" = "automated"
  }
}