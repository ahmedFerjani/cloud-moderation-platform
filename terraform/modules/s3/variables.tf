variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "purpose" {
  description = "Purpose of the S3 bucket"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "account_id" {
  description = "AWS Account ID"
  type        = string
}

variable "frontend_origins" {
  description = "List of allowed origins for S3 CORS"
  type        = list(string)
}
