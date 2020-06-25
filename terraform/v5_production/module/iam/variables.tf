variable "environment" {
    type = string
    description = "environment type (i.e dev, qa, uat, prod)"
}

variable "team" {
    type = string
    description = "name of the team (i.e datafence)"
}

variable "lambda_role_name" {
    type = string
    description = "Name of Lambda IAM Role"
    default = "lambda-role-automated"
}

variable "s3_policy_name" {
    type = string
    description = "Name of s3 policy"
    default = "s3_put_object_policy"
}

variable "s3_bucket_arn" {
    type = string
    description = "Arn of S3 Bucket"
}

