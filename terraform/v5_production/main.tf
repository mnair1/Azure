resource "aws_s3_bucket" "datafence_s3_bucket" {
  bucket = "${var.environment}-${var.team}-${var.s3_bucket_name}"

  tags = {
    Environment = var.environment
  }
}

module "iam_module" {
  source = "./module/iam"
  
  # module input variables
  environment = var.environment
  team = var.team
  s3_bucket_arn = aws_s3_bucket.datafence_s3_bucket.arn
}


resource "aws_lambda_function" "datafence_lambda_function" {
  filename = "lambda_codebase/lambda.zip"
  function_name = "${var.environment}-${var.team}-${var.lambda_name}"
  handler = "lambda_function.lambda_handler"
  role = module.iam_module.arn
  runtime = "python3.7"
  environment {
    variables = {
      bucket_name = aws_s3_bucket.datafence_s3_bucket.id
    }
  }
  tags = {
    "Environment" = var.environment
  }
}