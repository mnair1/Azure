resource "aws_lambda_function" "datafence_lambda_function" {
  filename = "lambda_codebase/lambda.zip"
  function_name = "devops-datafence-lambda-function-automated"
  handler = "lambda_function.lambda_handler"
  role = aws_iam_role.datafence_lambda_role.arn
  runtime = "python3.7"
  tags = {
    "Environment" = "automated"
  }
}