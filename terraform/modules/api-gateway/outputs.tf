output "api_id" {
  description = "ID of the API Gateway"
  value       = aws_apigatewayv2_api.this.id
}

output "api_execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_apigatewayv2_api.this.execution_arn
}

output "api_endpoint" {
  description = "Endpoint of the API Gateway"
  value       = aws_apigatewayv2_api.this.api_endpoint
}

output "api_domain_name" {
  description = "API Gateway invoke domain, without scheme (for use as a CloudFront origin)"
  value       = trimprefix(aws_apigatewayv2_api.this.api_endpoint, "https://")
}
