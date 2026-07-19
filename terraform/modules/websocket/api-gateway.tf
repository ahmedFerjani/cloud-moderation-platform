resource "aws_apigatewayv2_api" "this" {
  name                       = "${var.name_prefix}-ws"
  protocol_type              = "WEBSOCKET"
  description                = "Content moderation WebSocket API"
  route_selection_expression = "$request.body.action"
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/apigateway/${aws_apigatewayv2_api.this.name}"
  retention_in_days = 30
}

resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = var.environment != "prod"

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.this.arn
    format = jsonencode({
      requestId    = "$context.requestId"
      connectionId = "$context.connectionId"
      eventType    = "$context.eventType"
      routeKey     = "$context.routeKey"
      status       = "$context.status"
      requestTime  = "$context.requestTime"
      errorMessage = "$context.error.message"
    })
  }
}
