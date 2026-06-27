output "user_pool_id" {
  description = "Cognito user pool ID"
  value       = aws_cognito_user_pool.this.id
}

output "client_id" {
  description = "Cognito user pool client ID"
  value       = aws_cognito_user_pool_client.this.id
}

output "hosted_ui_url" {
  description = "Cognito hosted UI base URL"
  value       = "https://${aws_cognito_user_pool_domain.this.domain}.auth.${var.region}.amazoncognito.com"
}

output "jwt_audience" {
  description = "JWT audience"
  value       = aws_cognito_user_pool_client.this.id
}

output "jwt_issuer" {
  description = "JWT issuer URL"
  value       = "https://${aws_cognito_user_pool.this.endpoint}"
}
