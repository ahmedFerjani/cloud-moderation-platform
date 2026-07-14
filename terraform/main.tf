module "content_bucket" {
  source = "./modules/s3"

  account_id  = local.account_id
  name_prefix = local.name_prefix
  environment = var.environment
  purpose     = "uploads"
  region      = local.region

  cors_allowed_origins     = var.s3_frontend_origins
  enable_lifecycle_cleanup = true
}

module "moderation_table" {
  source = "./modules/dynamodb"

  name_prefix = local.name_prefix
  purpose     = "results"
}

module "sns" {
  source = "./modules/sns"

  name_prefix = local.name_prefix
  purpose     = "failures"

  notification_emails = var.notification_emails
}

module "sqs" {
  source = "./modules/sqs"

  name_prefix = local.name_prefix
}

module "lambda-layers" {
  source = "./modules/layers"

  name_prefix = local.name_prefix

  serverless_utils_zip_path = "${local.packages_dir}/serverless-utils.zip"
  image_processing_zip_path = "${local.packages_dir}/image-processing.zip"
}

module "api_lambda" {
  source = "./modules/lambdas/api"

  name_prefix = local.name_prefix
  environment = var.environment

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

  name_prefix = local.name_prefix
  environment = var.environment

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

  name_prefix = local.name_prefix
  environment = var.environment

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

  name_prefix = local.name_prefix
  environment = var.environment

  api_lambda_invoke_arn    = module.api_lambda.lambda_arn
  api_lambda_function_name = module.api_lambda.lambda_name

  jwt_issuer   = module.cognito.jwt_issuer
  jwt_audience = module.cognito.jwt_audience
}

module "cognito" {
  source = "./modules/cognito"

  project_name = var.project_name
  environment  = var.environment
  name_prefix  = local.name_prefix
  region       = local.region

  callback_urls = var.callback_urls
  logout_urls   = var.logout_urls
}

module "frontend_bucket" {
  source = "./modules/s3"

  account_id  = local.account_id
  name_prefix = local.name_prefix
  environment = var.environment
  purpose     = "static-site"
  region      = local.region

  enable_lifecycle_cleanup = false
}

module "cloudfront" {
  source = "./modules/cloudfront"

  name_prefix = local.name_prefix

  s3_bucket_regional_domain_name = module.frontend_bucket.bucket_regional_domain_name
  s3_bucket_id                   = module.frontend_bucket.bucket_id
  s3_bucket_arn                  = module.frontend_bucket.bucket_arn

  api_gateway_domain_name = module.api_gateway.api_domain_name
}
