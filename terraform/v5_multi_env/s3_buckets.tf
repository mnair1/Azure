resource "aws_s3_bucket" "datafence_s3_bucket" {
  #bucket = "devops-datafence-s3-bucket-automated"
  bucket = "${var.environment}-${var.team}-${var.s3_bucket_name}"

  tags = {
    Environment = "${var.environment}"
  }
}