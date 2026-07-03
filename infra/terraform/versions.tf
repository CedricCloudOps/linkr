terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }

  # Remote state. Create the bucket and lock table once, then uncomment.
  # backend "s3" {
  #   bucket         = "linkr-terraform-state"
  #   key            = "linkr/terraform.tfstate"
  #   region         = "eu-west-3"
  #   dynamodb_table = "linkr-terraform-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project   = var.project
      ManagedBy = "terraform"
    }
  }
}
