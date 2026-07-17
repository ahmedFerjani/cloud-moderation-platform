output "role_arn" {
  description = "ARN of the orchestrator lambda IAM role"
  value       = aws_iam_role.this.arn
}

output "role_name" {
  description = "Name of the orchestrator lambda IAM role"
  value       = aws_iam_role.this.name
}

output "lambda_arn" {
  description = "ARN of the Orchestrator Lambda"
  value       = aws_lambda_function.this.arn
}

output "lambda_name" {
  description = "Name of the Orchestrator Lambda"
  value       = aws_lambda_function.this.function_name
}

output "timeout" {
  description = "Timeout of the Orchestrator Lambda"
  value       = aws_lambda_function.this.timeout
}
