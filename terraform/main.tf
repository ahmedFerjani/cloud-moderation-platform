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
  purpose      = "results"
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
  purpose      = "failures"

  notification_emails = var.notification_emails
}

module "sqs" {
  source = "./modules/sqs"

  project_name = var.project_name
  environment  = var.environment
}

module "lambda-layers" {
  source = "./modules/layers"

  project_name = var.project_name
  environment  = var.environment

  serverless_utils_zip_path = "${local.packages_dir}/serverless-utils.zip"
  image_processing_zip_path = "${local.packages_dir}/image-processing.zip"
}

module "api_lambda" {
  source = "./modules/lambdas/api"

  project_name = var.project_name
  environment  = var.environment

  lambda_assume_role_json    = data.aws_iam_policy_document.lambda_assume_role.json
  lambda_basic_execution_arn = data.aws_iam_policy.lambda_basic_execution.arn

  api_lambda_zip_path        = "${local.packages_dir}/api.zip"
  serverless_utils_layer_arn = module.lambda-layers.serverless_utils_layer_arn

  content_bucket_name = module.content_bucket.bucket_name
  content_bucket_arn  = module.content_bucket.bucket_arn

  moderation_table_name = module.moderation_table.table_name
  moderation_table_arn  = module.moderation_table.table_arn
}

module "dql_handler_lambda" {
  source = "./modules/lambdas/dql_hanlder"

  project_name = var.project_name
  environment  = var.environment

  lambda_assume_role_json    = data.aws_iam_policy_document.lambda_assume_role.json
  lambda_basic_execution_arn = data.aws_iam_policy.lambda_basic_execution.arn

  dlq_handler_lambda_zip_path = "${local.packages_dir}/dlq-handler.zip"
  serverless_utils_layer_arn  = module.lambda-layers.serverless_utils_layer_arn

  dlq_arn           = module.sqs.dlq_arn
  failure_topic_arn = module.sns.topic_arn

  moderation_table_name = module.moderation_table.table_name
  moderation_table_arn  = module.moderation_table.table_arn
}
