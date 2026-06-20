variable "bucket_arn" {
  description = "ARN of the S3 bucket that will send messages to the SQS queue"
  type        = string
}


variable "bucket_id" {
  description = "ID of the S3 bucket that will send messages to the SQS queue"
  type        = string
}

variable "main_queue_url" {
  description = "URL of the main SQS queue"
  type        = string
}

variable "main_queue_arn" {
  description = "ARN of the main SQS queue"
  type        = string
}

variable "dlq_arn" {
  description = "ARN of the dead-letter queue (DLQ)"
  type        = string
}

variable "orchestrator_lambda_arn" {
  description = "ARN of the orchestrator Lambda function"
  type        = string
}

variable "dlq_handler_lambda_arn" {
  description = "ARN of the Lambda function that handles messages from the DLQ"
  type        = string
}
