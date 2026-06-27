variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "runtime" {
  description = "Runtime for DLQ Handler Lambda"
  type        = string
  default     = "python3.14"
}

variable "dlq_handler_lambda_zip_path" {
  description = "Path to the DLQ Handler Lambda zip file"
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

variable "dlq_arn" {
  description = "ARN of the SQS dead-letter queue"
  type        = string
}

variable "moderation_table_arn" {
  description = "ARN of the DynamoDB table for moderation results"
  type        = string
}

variable "moderation_table_name" {
  description = "Name of the DynamoDB table for moderation results"
  type        = string
}

variable "failure_topic_arn" {
  description = "ARN of the SNS topic for failure notifications"
  type        = string
}
