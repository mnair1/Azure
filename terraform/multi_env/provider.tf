terraform {
  backend s3 {
      bucket = "devops-datafence-tf-backend"
      region = "us-east-1"
      key = "remote_state_file.tfstate"
  }
  required_providers {
    aws = "~> 2.66.0"
  }
}

provider "aws" {
  region = "us-east-1"
}
