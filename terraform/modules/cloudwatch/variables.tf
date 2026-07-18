variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "sns_topic_arn" {
  type        = string
  description = "SNS topic ARN to notify when an alarm enters ALARM state"
}

variable "lambdas" {
  type = map(object({
    function_name = string
    timeout       = number
  }))
  description = "Map of Lambda functions to monitor"
}

variable "dlq_name" {
  type        = string
  description = "Name of the dead-letter queue to monitor"
}

variable "api_gateway_id" {
  type        = string
  description = "API Gateway ID to monitor"
}
