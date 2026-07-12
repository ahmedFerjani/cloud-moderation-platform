output "content_bucket_name" {
  value = module.content_bucket.bucket_name
}

output "content_bucket_arn" {
  value = module.content_bucket.bucket_arn
}

output "moderation_table_name" {
  value = module.moderation_table.table_name
}

output "moderation_table_arn" {
  value = module.moderation_table.table_arn
}

output "cognito_login_url" {
  description = "Cognito login URL"
  value       = "${module.cognito.hosted_ui_url}/login?client_id=${module.cognito.client_id}&response_type=code&scope=email+openid+profile&redirect_uri=${var.callback_urls[0]}"
}

output "frontend_bucket_regional_domain_name" {
  value = module.frontend_bucket.bucket_regional_domain_name
}

output "cloudfront_domain_name" {
  description = "CloudFront distribution domain name for the frontend"
  value       = module.cloudfront.distribution_domain_name
}
