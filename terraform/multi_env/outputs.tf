output "s3_bucket_arn" {
    value = "${aws_s3_bucket.datafence_s3_bucket.arn}"
}

output "lambda_arn" {
    value = "${aws_lambda_function.datafence_lambda_function.arn}"
}