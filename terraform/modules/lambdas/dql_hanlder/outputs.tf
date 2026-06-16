output "role_arn" {
  description = "ARN of the DQL handler lambda IAM role"
  value       = aws_iam_role.this.arn
}

output "role_name" {
  description = "Name of the DQL handler lambda IAM role"
  value       = aws_iam_role.this.name
}

output "lambda_arn" {
  description = "ARN of the DQL handler Lambda"
  value       = aws_lambda_function.this.arn
}

output "lambda_name" {
  description = "Name of the DQL handler Lambda"
  value       = aws_lambda_function.this.function_name
}
