output "role_arn" {
  description = "ARN of the api lambda IAM role"
  value       = aws_iam_role.this.arn
}

output "role_name" {
  description = "Name of the api lambda IAM role"
  value       = aws_iam_role.this.name
}
