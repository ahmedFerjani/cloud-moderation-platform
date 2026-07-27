resource "aws_cloudfront_function" "spa_fallback" {
  name    = "${var.name_prefix}-spa-fallback"
  runtime = "cloudfront-js-2.0"
  comment = "Rewrites extensionless paths to index.html for Angular routing"
  publish = true
  code    = file("${path.module}/functions/spa-fallback.js")
}

resource "aws_cloudfront_function" "strip_api_prefix" {
  name    = "${var.name_prefix}-strip-api-prefix"
  runtime = "cloudfront-js-2.0"
  comment = "Strips /api prefix before forwarding requests to API Gateway"
  publish = true
  code    = file("${path.module}/functions/strip-api-prefix.js")
}

resource "aws_cloudfront_function" "strip_ws_prefix" {
  name    = "${var.name_prefix}-strip-ws-prefix"
  runtime = "cloudfront-js-2.0"
  comment = "Strips /ws prefix before forwarding requests to WebSocket API Gateway"
  publish = true
  code    = file("${path.module}/functions/strip-ws-prefix.js")
}
