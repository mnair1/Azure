variable "s3_bucket_name" {
    type = "string"
    description = "name of s3 bucket"
    #default = "devops-datafence-s3-bucket-automated"
}

variable "lambda_role_name" {
    type = "string"
    description = "Name of Lambda IAM Role"
    #default = "devops-datafence-lambda-role-automated"
}

variable "lambda_name" {
    type = "string"
    description = "Name of lambda function"
    #default = "devops-datafence-lambda-function-automated"
}