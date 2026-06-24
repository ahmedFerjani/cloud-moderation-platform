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

  lambda_assume_role_json    = local.lambda_assume_role_json
  lambda_basic_execution_arn = local.lambda_basic_execution_arn

  api_lambda_zip_path        = "${local.packages_dir}/api.zip"
  serverless_utils_layer_arn = module.lambda-layers.serverless_utils_layer_arn

  content_bucket_name = module.content_bucket.bucket_name
  content_bucket_arn  = module.content_bucket.bucket_arn

  moderation_table_name = module.moderation_table.table_name
  moderation_table_arn  = module.moderation_table.table_arn
}

module "dlq_handler_lambda" {
  source = "./modules/lambdas/dlq_hanlder"

  project_name = var.project_name
  environment  = var.environment

  lambda_assume_role_json    = local.lambda_assume_role_json
  lambda_basic_execution_arn = local.lambda_basic_execution_arn

  dlq_handler_lambda_zip_path = "${local.packages_dir}/dlq-handler.zip"
  serverless_utils_layer_arn  = module.lambda-layers.serverless_utils_layer_arn

  dlq_arn           = module.sqs.dlq_arn
  failure_topic_arn = module.sns.topic_arn

  moderation_table_name = module.moderation_table.table_name
  moderation_table_arn  = module.moderation_table.table_arn
}

module "orchestrator_lambda" {
  source = "./modules/lambdas/orchestrator"

  environment  = var.environment
  project_name = var.project_name

  lambda_assume_role_json    = local.lambda_assume_role_json
  lambda_basic_execution_arn = local.lambda_basic_execution_arn

  orchestrator_lambda_zip_path = "${local.packages_dir}/orchestrator.zip"
  serverless_utils_layer_arn   = module.lambda-layers.serverless_utils_layer_arn
  image_processing_lambda_arn  = module.lambda-layers.image_processing_layer_arn

  bucket_owner_id       = local.account_id
  content_bucket_arn    = module.content_bucket.bucket_arn
  moderation_table_arn  = module.moderation_table.table_arn
  moderation_table_name = module.moderation_table.table_name

  main_queue_arn = module.sqs.main_queue_arn
}

module "triggers" {
  source = "./modules/triggers"

  bucket_id  = module.content_bucket.bucket_id
  bucket_arn = module.content_bucket.bucket_arn

  main_queue_url = module.sqs.main_queue_url
  main_queue_arn = module.sqs.main_queue_arn
  dlq_arn        = module.sqs.dlq_arn

  orchestrator_lambda_arn = module.orchestrator_lambda.lambda_arn
  dlq_handler_lambda_arn  = module.dlq_handler_lambda.lambda_arn
}

module "api_gateway" {
  source = "./modules/api-gateway"

  project_name = var.project_name
  environment  = var.environment

  api_lambda_invoke_arn    = module.api_lambda.lambda_arn
  api_lambda_function_name = module.api_lambda.lambda_name
}
