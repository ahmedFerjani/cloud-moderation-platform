resource "aws_iam_role" "disconnect" {
  name               = "${var.name_prefix}-websocket-disconnect-lambda-role"
  assume_role_policy = var.lambda_assume_role_json
}

resource "aws_iam_role_policy_attachment" "disconnect" {
  role       = aws_iam_role.disconnect.name
  policy_arn = var.lambda_basic_execution_arn
}

resource "aws_iam_role_policy" "disconnect" {
  name   = "${var.name_prefix}-websocket-disconnect-lambda-policy"
  role   = aws_iam_role.disconnect.id
  policy = data.aws_iam_policy_document.disconnect.json
}

resource "aws_cloudwatch_log_group" "disconnect" {
  name              = "/aws/lambda/${aws_lambda_function.disconnect.function_name}"
  retention_in_days = 30
}

resource "aws_lambda_function" "disconnect" {
  function_name = "${var.name_prefix}-websocket-disconnect-lambda"
  role          = aws_iam_role.disconnect.arn

  handler       = "handler.lambda_handler"
  runtime       = var.runtime
  architectures = ["arm64"]

  memory_size = 128
  timeout     = 5

  layers = [var.serverless_utils_layer_arn]

  filename         = var.websocket_disconnect_lambda_zip_path
  source_code_hash = filebase64sha256(var.websocket_disconnect_lambda_zip_path)

  environment {
    variables = {
      CAPTURE_SAMPLE_EVENTS = tostring(var.environment == "dev")
      CONNECTIONS_TABLE_NAME = aws_dynamodb_table.this.name
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.disconnect,
    aws_iam_role_policy.disconnect,
  ]
}

resource "aws_apigatewayv2_integration" "disconnect" {
  api_id             = aws_apigatewayv2_api.this.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.disconnect.invoke_arn
  integration_method = "POST"
}

resource "aws_lambda_permission" "allow_disconnect_invoke" {
  statement_id  = "AllowWebSocketDisconnectInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.disconnect.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*/$disconnect"
}

resource "aws_apigatewayv2_route" "disconnect" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "$disconnect"
  target    = "integrations/${aws_apigatewayv2_integration.disconnect.id}"
}
