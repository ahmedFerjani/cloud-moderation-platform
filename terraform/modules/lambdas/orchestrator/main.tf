resource "aws_iam_role" "this" {
  name               = lower("${var.project_name}-${var.environment}-orchestrator-lambda-role")
  assume_role_policy = var.lambda_assume_role_json
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.this.name
  policy_arn = var.lambda_basic_execution_arn
}

resource "aws_iam_role_policy" "orchestrator_lambda_policy" {
  name   = lower("${var.project_name}-${var.environment}-orchestrator-lambda-policy")
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.orchestrator_lambda_policy.json
}

resource "aws_cloudwatch_log_group" "this" {
  name              = lower("/aws/lambda/${var.project_name}-${var.environment}-orchestrator-lambda")
  retention_in_days = 30
}

resource "aws_lambda_function" "this" {
  function_name = lower("${var.project_name}-${var.environment}-orchestrator-lambda")
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
      CAPTURE_SAMPLE_EVENTS = tostring(var.environment == "dev")
      EXPECTED_BUCKET_OWNER = var.bucket_owner_id
      TABLE_NAME            = var.moderation_table_name
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.basic,
    aws_iam_role_policy.orchestrator_lambda_policy,
  ]
}
