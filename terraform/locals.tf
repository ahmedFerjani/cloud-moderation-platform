locals {
  default_tags = {
    Project     = "content-moderation"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Owner       = "Ahmed Ferjani"
  }

  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.region

  name_prefix = lower("${var.project_name}-${var.environment}")

  lambda_assume_role_json    = data.aws_iam_policy_document.lambda_assume_role.json
  lambda_basic_execution_arn = data.aws_iam_policy.lambda_basic_execution.arn

  packages_dir = "${path.module}/../backend/packages"
}
