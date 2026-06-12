provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "content-moderation"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "Ahmed Ferjani"
    }
  }
}
