resource "aws_s3_bucket" "datafence_s3_bucket" {
  bucket = "devops-datafence-s3-bucket-automated"

  tags = {
    Environment = "automated"
  }
}