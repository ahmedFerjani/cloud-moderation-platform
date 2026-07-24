resource "aws_iam_role" "this" {
  name               = "${var.name_prefix}-orchestrator-lambda-role"
  assume_role_policy = var.lambda_assume_role_json
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.this.name
  policy_arn = var.lambda_basic_execution_arn
}

resource "aws_iam_role_policy" "orchestrator_lambda_policy" {
  name   = "${var.name_prefix}-orchestrator-lambda-policy"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.orchestrator_lambda_policy.json
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${aws_lambda_function.this.function_name}"
  retention_in_days = 30
}

resource "aws_lambda_function" "this" {
  function_name = "${var.name_prefix}-orchestrator-lambda"
  role          = aws_iam_role.this.arn

  handler       = "handler.lambda_handler"
  runtime       = var.runtime
  architectures = ["arm64"]

  memory_size = 512
  timeout     = 30

  layers = [
    var.serverless_utils_layer_arn,
    var.image_processing_lambda_arn
  ]

  filename         = var.orchestrator_lambda_zip_path
  source_code_hash = filebase64sha256(var.orchestrator_lambda_zip_path)

  environment {
    variables = {
      CAPTURE_SAMPLE_EVENTS  = tostring(var.environment == "dev")
      EXPECTED_BUCKET_OWNER  = var.bucket_owner_id
      TABLE_NAME             = var.moderation_table_name
      CONNECTIONS_TABLE_NAME = var.connections_table_name
      WEBSOCKET_ENDPOINT_URL = var.websocket_management_endpoint
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.basic,
    aws_iam_role_policy.orchestrator_lambda_policy,
  ]
}
