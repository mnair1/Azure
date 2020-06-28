terraform {
  backend s3 {
      bucket = "devops-datafence-tf-backend"
      key = "terraform_state"
      dynamodb_table = "lock_table"
      region = "us-east-1"
      
  }
  required_providers {
    aws = "2.66.0"
  }
}

provider "aws" {
  region = "us-east-1"
}
