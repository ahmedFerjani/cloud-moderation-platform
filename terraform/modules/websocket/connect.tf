resource "aws_iam_role" "connect" {
  name               = "${var.name_prefix}-websocket-connect-lambda-role"
  assume_role_policy = var.lambda_assume_role_json
}

resource "aws_iam_role_policy_attachment" "connect" {
  role       = aws_iam_role.connect.name
  policy_arn = var.lambda_basic_execution_arn
}

resource "aws_iam_role_policy" "connect" {
  name   = "${var.name_prefix}-websocket-connect-lambda-policy"
  role   = aws_iam_role.connect.id
  policy = data.aws_iam_policy_document.connect.json
}

resource "aws_cloudwatch_log_group" "connect" {
  name              = "/aws/lambda/${aws_lambda_function.connect.function_name}"
  retention_in_days = 30
}

resource "aws_lambda_function" "connect" {
  function_name = "${var.name_prefix}-websocket-connect-lambda"
  role          = aws_iam_role.connect.arn

  handler       = "handler.lambda_handler"
  runtime       = var.runtime
  architectures = ["arm64"]

  memory_size = 128
  timeout     = 5

  layers = [var.serverless_utils_layer_arn]

  filename         = var.websocket_connect_lambda_zip_path
  source_code_hash = filebase64sha256(var.websocket_connect_lambda_zip_path)

  environment {
    variables = {
      CAPTURE_SAMPLE_EVENTS = tostring(var.environment == "dev")
      CONNECTIONS_TABLE_NAME = aws_dynamodb_table.this.name
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.connect,
    aws_iam_role_policy.connect,
  ]
}

resource "aws_apigatewayv2_integration" "connect" {
  api_id             = aws_apigatewayv2_api.this.id
  integration_type   = "AWS_PROXY"
  integration_uri    = aws_lambda_function.connect.invoke_arn
  integration_method = "POST"
}

resource "aws_lambda_permission" "allow_connect_invoke" {
  statement_id  = "AllowWebSocketConnectInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.connect.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*/$connect"
}

resource "aws_apigatewayv2_route" "connect" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "$connect"
  target    = "integrations/${aws_apigatewayv2_integration.connect.id}"
}
