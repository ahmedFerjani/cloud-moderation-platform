output "serverless_utils_layer_arn" {
  description = "ARN of the serverless utils Lambda layer"
  value       = aws_lambda_layer_version.serverless_utils.arn
}

output "image_processing_layer_arn" {
  description = "ARN of the Image Processing Lambda layer"
  value       = aws_lambda_layer_version.image_processing.arn
}
