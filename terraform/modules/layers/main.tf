resource "aws_lambda_layer_version" "serverless_utils" {
  layer_name  = lower("${var.project_name}-${var.environment}-serverless-utils")
  description = "Shared Python utilities: logger, encoders, response helpers"

  filename         = var.serverless_utils_zip_path
  source_code_hash = filebase64sha256(var.serverless_utils_zip_path)

  compatible_runtimes      = var.runtime
  compatible_architectures = var.serverless_utils_compatible_architectures

  license_info = "MIT"
}

resource "aws_lambda_layer_version" "image_processing" {
  layer_name  = lower("${var.project_name}-${var.environment}-image-processing")
  description = "Image processing dependencies layer"

  filename         = var.image_processing_zip_path
  source_code_hash = filebase64sha256(var.image_processing_zip_path)

  compatible_runtimes      = var.runtime
  compatible_architectures = var.image_processing_compatible_architectures

  license_info = "HPND"
}
