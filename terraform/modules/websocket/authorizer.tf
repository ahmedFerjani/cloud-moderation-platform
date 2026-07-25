resource "aws_iam_role" "authorizer" {
  name               = "${var.name_prefix}-websocket-authorizer-lambda-role"
  assume_role_policy = var.lambda_assume_role_json
}

resource "aws_iam_role_policy_attachment" "authorizer" {
  role       = aws_iam_role.authorizer.name
  policy_arn = var.lambda_basic_execution_arn
}

resource "aws_cloudwatch_log_group" "authorizer" {
  name              = "/aws/lambda/${aws_lambda_function.authorizer.function_name}"
  retention_in_days = 30
}

resource "aws_lambda_function" "authorizer" {
  function_name = "${var.name_prefix}-websocket-authorizer-lambda"
  role          = aws_iam_role.authorizer.arn

  handler       = "handler.lambda_handler"
  runtime       = var.runtime
  architectures = ["arm64"]

  memory_size = 128
  timeout     = 5

  layers = [
    var.serverless_utils_layer_arn,
    var.jwt_auth_layer_arn
  ]

  filename         = var.websocket_authorizer_lambda_zip_path
  source_code_hash = filebase64sha256(var.websocket_authorizer_lambda_zip_path)

  environment {
    variables = {
      CAPTURE_SAMPLE_EVENTS = tostring(var.environment == "dev")
      USER_POOL_ID          = var.cognito_user_pool_id
      APP_CLIENT_ID         = var.cognito_client_id
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.authorizer,
  ]
}

resource "aws_apigatewayv2_authorizer" "this" {
  api_id                            = aws_apigatewayv2_api.this.id
  authorizer_type                   = "REQUEST"
  name                              = "${var.name_prefix}-websocket-jwt-authorizer"
  authorizer_uri                    = aws_lambda_function.authorizer.invoke_arn
  identity_sources                  = ["route.request.querystring.token"]
}

resource "aws_lambda_permission" "allow_authorizer_invoke" {
  statement_id  = "AllowWebSocketAuthorizerInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.authorizer.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/authorizers/${aws_apigatewayv2_authorizer.this.id}"
}
