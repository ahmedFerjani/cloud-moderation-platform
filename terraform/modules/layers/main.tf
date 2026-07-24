resource "aws_lambda_layer_version" "serverless_utils" {
  layer_name  = "${var.name_prefix}-serverless-utils"
  description = "Shared Python utilities: logger, encoders, response helpers"

  filename         = var.serverless_utils_zip_path
  source_code_hash = filebase64sha256(var.serverless_utils_zip_path)

  compatible_runtimes      = var.runtime
  compatible_architectures = var.serverless_utils_compatible_architectures

  license_info = "MIT"
}

resource "aws_lambda_layer_version" "image_processing" {
  layer_name  = "${var.name_prefix}-image-processing"
  description = "Image processing dependencies layer"

  filename         = var.image_processing_zip_path
  source_code_hash = filebase64sha256(var.image_processing_zip_path)

  compatible_runtimes      = var.runtime
  compatible_architectures = var.image_processing_compatible_architectures

  license_info = "HPND"
}

resource "aws_lambda_layer_version" "jwt_auth" {
  layer_name  = "${var.name_prefix}-jwt-auth"
  description = "JWT authentication dependencies layer"

  filename         = var.jwt_auth_zip_path
  source_code_hash = filebase64sha256(var.jwt_auth_zip_path)

  compatible_runtimes      = var.runtime
  compatible_architectures = var.jwt_auth_compatible_architectures

  license_info = "MIT"
}
