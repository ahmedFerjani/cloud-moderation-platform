resource "aws_apigatewayv2_api" "this" {
  name          = lower("${var.project_name}-${var.environment}")
  protocol_type = "HTTP"
  description   = "Content moderation API"
}

resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = var.environment != "prod"
}
