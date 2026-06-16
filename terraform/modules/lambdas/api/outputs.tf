output "role_arn" {
  description = "ARN of the api lambda IAM role"
  value       = aws_iam_role.this.arn
}

output "role_name" {
  description = "Name of the api lambda IAM role"
  value       = aws_iam_role.this.name
}

output "lambda_arn" {
  description = "ARN of the API Lambda"
  value       = aws_lambda_function.this.arn
}

output "lambda_name" {
  description = "Name of the API Lambda"
  value       = aws_lambda_function.this.function_name
}
