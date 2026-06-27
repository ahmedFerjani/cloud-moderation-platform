variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "api_lambda_invoke_arn" {
  description = "ARN of the API Lambda function to be invoked by the API Gateway"
  type        = string
}

variable "api_lambda_function_name" {
  description = "Name of the API Lambda function to be invoked by the API Gateway"
  type        = string
}
