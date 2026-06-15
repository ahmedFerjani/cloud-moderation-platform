resource "aws_lambda_layer_version" "serverless_utils" {
  layer_name = lower(
    "${var.project_name}-${var.environment}-serverless-utils"
  )
  filename = var.serverless_utils_zip_path

  compatible_runtimes      = var.serverless_utils_runtime
  compatible_architectures = var.serverless_utils_compatible_architectures
}

resource "aws_lambda_layer_version" "image_processing" {
  layer_name = lower(
    "${var.project_name}-${var.environment}-image-processing"
  )
  filename = var.image_processing_zip_path

  compatible_runtimes      = var.image_processing_runtime
  compatible_architectures = var.image_processing_compatible_architectures
}
