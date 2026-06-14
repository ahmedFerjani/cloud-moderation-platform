variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "purpose" {
  description = "Purpose of the SNS topic"
  type        = string
}

variable "notification_emails" {
  description = "List of email addresses to receive failure notifications"
  type        = list(string)
}