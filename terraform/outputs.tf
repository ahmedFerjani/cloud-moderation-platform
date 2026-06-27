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
