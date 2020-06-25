variable "environment" {
    type = string
    description = "environment type (i.e dev, qa, uat, prod)"
}

variable "team" {
    type = string
    description = "name of the team (i.e datafence)"
}

variable "s3_bucket_name" {
    type = string
    description = "name of s3 bucket"
    #default = "devops-datafence-s3-bucket-automated"
}

variable "lambda_name" {
    type = string
    description = "Name of lambda function"
    #default = "devops-datafence-lambda-function-automated"
}
