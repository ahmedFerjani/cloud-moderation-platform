variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "message_retention_seconds_dlq_queue" {
  description = "Message retention period for the dead-letter SQS queue in seconds"
  type        = number
  default     = 1209600 # 14 days
}

variable "message_retention_seconds_main_queue" {
  description = "Message retention period for the main SQS queue in seconds"
  type        = number
  default     = 345600 # 4 days
}

variable "visibility_timeout_seconds" {
  description = "Visibility timeout for the main SQS queue in seconds"
  type        = number
  default     = 30
}

variable "max_receive_count" {
  description = "Maximum number of times a message can be received before being sent to the dead-letter queue"
  type        = number
  default     = 5
}
