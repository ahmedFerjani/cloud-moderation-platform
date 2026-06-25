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
