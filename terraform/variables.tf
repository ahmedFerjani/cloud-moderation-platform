variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "content-moderation"
}

variable "notification_emails" {
  description = "List of email addresses to receive failure notifications"
  type        = list(string)
}

variable "s3_frontend_origins" {
  description = "List of allowed origins for S3 CORS"
  type        = list(string)
}

variable "callback_urls" {
  description = "List of allowed callback URLs for the Cognito app client"
  type        = list(string)
}

variable "logout_urls" {
  description = "List of allowed logout URLs for the Cognito app client"
  type        = list(string)
}

variable "waf_rate_limit" {
  description = "Max requests per 5-minute window per IP before blocking"
  type        = number
  default     = 2000
}
