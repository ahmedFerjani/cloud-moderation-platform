variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "runtime" {
  description = "Runtime for WebSocket lambdas"
  type        = string
  default     = "python3.14"
}

variable "websocket_connect_lambda_zip_path" {
  description = "Path to the WebSocket Connect Lambda zip file"
  type        = string
}

variable "websocket_disconnect_lambda_zip_path" {
  description = "Path to the WebSocket Disconnect Lambda zip file"
  type        = string
}

variable "serverless_utils_layer_arn" {
  description = "ARN of the serverless utils layer"
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
