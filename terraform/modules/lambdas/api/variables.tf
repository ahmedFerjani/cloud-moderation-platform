variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "runtime" {
  description = "Runtime for API Lambda"
  type        = string
  default     = "python3.14"
}

variable "api_lambda_zip_path" {
  description = "Path to the API Lambda zip file"
  type        = string
}

variable "serverless_utils_layer_arn" {
  description = "ARN of the serverless utils layer"
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

variable "content_bucket_name" {
  description = "Name of the S3 bucket for content storage"
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
