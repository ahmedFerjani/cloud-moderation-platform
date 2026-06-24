resource "aws_apigatewayv2_api" "this" {
  name          = lower("${var.project_name}-${var.environment}")
  protocol_type = "HTTP"
  description   = "Content moderation API"
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/apigateway/${lower("${var.project_name}-${var.environment}")}"
  retention_in_days = 30
}

resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = var.environment != "prod"

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.this.arn
    format = jsonencode({
      requestId        = "$context.requestId"
      sourceIp         = "$context.identity.sourceIp"
      requestTime      = "$context.requestTime"
      httpMethod       = "$context.httpMethod"
      routeKey         = "$context.routeKey"
      status           = "$context.status"
      protocol         = "$context.protocol"
      responseLength   = "$context.responseLength"
      errorMessage     = "$context.error.message"
      integrationError = "$context.integrationErrorMessage"
    })
  }
}
