module "content_bucket" {
  source = "./modules/s3"

  account_id   = local.account_id
  environment  = var.environment
  project_name = var.project_name
  purpose      = "uploads"
  region       = local.region
}

module "moderation_table" {
  source = "./modules/dynamodb"

  environment  = var.environment
  project_name = var.project_name
  purpose      = "moderation-results"
}

module "api_lambda" {
  source = "./modules/lambdas/api"

  environment  = var.environment
  project_name = var.project_name

  lambda_assume_role_json    = data.aws_iam_policy_document.lambda_assume_role.json
  lambda_basic_execution_arn = data.aws_iam_policy.lambda_basic_execution.arn

  content_bucket_arn           = module.content_bucket.bucket_arn
  moderation_results_table_arn = module.moderation_table.table_arn
}

module "orchestrator_lambda" {
  source = "./modules/lambdas/orchestrator"

  environment  = var.environment
  project_name = var.project_name

  lambda_assume_role_json    = data.aws_iam_policy_document.lambda_assume_role.json
  lambda_basic_execution_arn = data.aws_iam_policy.lambda_basic_execution.arn

  content_bucket_arn           = module.content_bucket.bucket_arn
  moderation_results_table_arn = module.moderation_table.table_arn
}

module "sns" {
  source = "./modules/sns"

  project_name = var.project_name
  environment  = var.environment
  purpose      = "moderation-failures"

  notification_emails = var.notification_emails
}

module "sqs" {
  source = "./modules/sqs"

  project_name = var.project_name
  environment  = var.environment
}
