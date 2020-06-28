resource "aws_s3_bucket" "datafence_s3_bucket" {
  bucket = var.s3_bucket_name

  tags = {
    Environment = "automated"
  }
}