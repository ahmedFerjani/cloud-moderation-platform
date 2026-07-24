output "connections_table_name" {
  description = "Name of the WebSocket connections table"
  value       = aws_dynamodb_table.this.name
}

output "connections_table_arn" {
  description = "ARN of the WebSocket connections table"
  value       = aws_dynamodb_table.this.arn
}

output "websocket_execution_arn" {
  description = "Execution ARN of the WebSocket API, for IAM permission scoping"
  value       = aws_apigatewayv2_api.this.execution_arn
}

output "websocket_management_endpoint" {
  description = "HTTPS endpoint for the API Gateway Management API, used by PostToConnection"
  value       = replace(aws_apigatewayv2_stage.this.invoke_url, "wss://", "https://")
}
