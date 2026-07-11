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

variable "cors_allowed_origins" {
  description = "List of allowed origins for S3 CORS"
  type        = list(string)
  default     = []
}

variable "enable_lifecycle_cleanup" {
  description = "Whether to enable lifecycle cleanup for the S3 bucket"
  type        = bool
  default     = false
}
