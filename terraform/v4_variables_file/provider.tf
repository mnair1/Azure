terraform {
  required_providers {
    aws = "~> 2.66.0"
  }
}

provider "aws" {
  region = "us-east-1"
}
