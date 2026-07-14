resource "aws_cloudfront_function" "strip_api_prefix" {
  name    = "${var.name_prefix}-strip-api-prefix"
  runtime = "cloudfront-js-2.0"
  comment = "Strips /api prefix before forwarding requests to API Gateway"
  publish = true
  code    = file("${path.module}/functions/strip-api-prefix.js")
}
