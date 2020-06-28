terraform {
  required_providers {
    aws = var.aws_provider_version
  }
}

provider "aws" {
  region = var.region
}
