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
