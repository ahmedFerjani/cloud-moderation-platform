variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "sns_topic_arn" {
  type        = string
  description = "SNS topic ARN to notify when an alarm enters ALARM state"
}

variable "lambda_function_names" {
  type        = map(string)
  description = "Map of Lambda function names to monitor"
}
