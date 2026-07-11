resource "aws_cloudfront_origin_access_control" "this" {
  name                              = "${var.name_prefix}-frontend-oac"
  description                       = "Origin Access Control for the CloudFront distribution"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
