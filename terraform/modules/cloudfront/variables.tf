variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
}

variable "s3_bucket_regional_domain_name" {
  description = "The regional domain name of the S3 bucket to be used as the origin for the CloudFront distribution"
  type        = string
}

variable "s3_bucket_id" {
  description = "The ID of the S3 bucket to be used as the origin for the CloudFront distribution"
  type        = string
}

variable "s3_bucket_arn" {
  description = "The ARN of the S3 bucket to be used as the origin for the CloudFront distribution"
  type        = string
}

variable "api_gateway_domain_name" {
  description = "The domain name of the API Gateway to be used as the origin for the CloudFront distribution"
  type        = string
}

variable "web_acl_arn" {
  description = "ARN of the WAF Web ACL to associate with this distribution"
  type        = string
}
