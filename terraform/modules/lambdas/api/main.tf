resource "aws_iam_role" "this" {
  name               = lower("${var.project_name}-${var.environment}-api-lambda-role")
  assume_role_policy = var.lambda_assume_role_json
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.this.name
  policy_arn = var.lambda_basic_execution_arn
}

resource "aws_iam_role_policy" "api_lambda_policy" {
  name   = lower("${var.project_name}-${var.environment}-api-lambda-policy")
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.api_lambda_policy.json
}

resource "aws_cloudwatch_log_group" "this" {
  name              = lower("/aws/lambda/${var.project_name}-${var.environment}-api-lambda")
  retention_in_days = 30
}

resource "aws_lambda_function" "this" {
  function_name = lower("${var.project_name}-${var.environment}-api-lambda")
  role          = aws_iam_role.this.arn

  depends_on = [
    aws_iam_role_policy_attachment.basic,
    aws_iam_role_policy.api_lambda_policy,
  ]

  handler       = "handler.lambda_handler"
  runtime       = var.runtime
  architectures = ["arm64"]

  memory_size = 512
  timeout     = 30

  layers = [var.serverless_utils_layer_arn]

  filename         = var.api_lambda_zip_path
  source_code_hash = filebase64sha256(var.api_lambda_zip_path)

  environment {
    variables = {
      BUCKET_NAME           = var.content_bucket_name
      TABLE_NAME            = var.moderation_results_table_name
      CAPTURE_SAMPLE_EVENTS = tostring(var.environment == "dev")
    }
  }
}
