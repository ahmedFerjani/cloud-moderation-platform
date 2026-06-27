variable "project_name" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Deployment environment"
  type        = string
}

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}

variable "callback_urls" {
  description = "List of allowed callback URLs for the Cognito app client"
  type        = list(string)
}

variable "logout_urls" {
  description = "List of allowed logout URLs for the Cognito app client"
  type        = list(string)
}
