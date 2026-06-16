variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "runtime" {
  description = "Runtime for Orchestrator Lambda"
  type        = string
  default     = "python3.14"
}

variable "orchestrator_lambda_zip_path" {
  description = "Path to the Orchestrator Lambda zip file"
  type        = string
}

variable "serverless_utils_layer_arn" {
  description = "ARN of the serverless utils layer"
  type        = string
}

variable "image_processing_lambda_arn" {
  description = "ARN of the Image Processing Lambda"
  type        = string
}

variable "lambda_assume_role_json" {
  description = "IAM trust policy JSON allowing Lambda service to assume this role"
  type        = string
}

variable "lambda_basic_execution_arn" {
  description = "ARN of the AWS managed policy for basic Lambda execution"
  type        = string
}

variable "bucket_owner_id" {
  description = "AWS Account ID of the S3 bucket owner"
  type        = string
}

variable "content_bucket_arn" {
  description = "ARN of the S3 bucket for content storage"
  type        = string
}

variable "moderation_table_name" {
  description = "Name of the DynamoDB table for moderation results"
  type        = string
}

variable "moderation_table_arn" {
  description = "ARN of the DynamoDB table for moderation results"
  type        = string
}
