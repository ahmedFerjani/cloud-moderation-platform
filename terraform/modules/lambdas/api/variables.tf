variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
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

variable "content_bucket_arn" {
  description = "ARN of the S3 bucket for content storage"
  type        = string
}

variable "moderation_results_table_arn" {
  description = "ARN of the DynamoDB table for moderation results"
  type        = string
}
