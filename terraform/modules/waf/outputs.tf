output "web_acl_arn" {
  description = "ARN of the WAF Web ACL, for attaching to a CloudFront distribution"
  value       = aws_wafv2_web_acl.this.arn
}
