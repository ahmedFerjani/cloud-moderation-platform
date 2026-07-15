variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "rate_limit" {
  description = "Max requests per 5-minute window per IP before blocking"
  type        = number
  default     = 2000
}
