resource "aws_wafv2_web_acl_rule" "rate_limit" {
  name        = "RateLimit"
  priority    = 1
  web_acl_arn = aws_wafv2_web_acl.this.arn

  action {
    block {}
  }

  statement {
    rate_based_statement {
      limit              = var.rate_limit
      aggregate_key_type = "IP"
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.name_prefix}-rate-limit"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl_rule" "ip_reputation" {
  name        = "AWSManagedRulesAmazonIpReputationList"
  priority    = 2
  web_acl_arn = aws_wafv2_web_acl.this.arn

  override_action {
    none {}
  }

  statement {
    managed_rule_group_statement {
      name        = "AWSManagedRulesAmazonIpReputationList"
      vendor_name = "AWS"
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.name_prefix}-ip-reputation"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl_rule" "common_rule_set" {
  name        = "AWSManagedRulesCommonRuleSet"
  priority    = 3
  web_acl_arn = aws_wafv2_web_acl.this.arn

  override_action {
    none {}
  }

  statement {
    managed_rule_group_statement {
      name        = "AWSManagedRulesCommonRuleSet"
      vendor_name = "AWS"
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.name_prefix}-common-rule-set"
    sampled_requests_enabled   = true
  }
}

resource "aws_wafv2_web_acl_rule" "known_bad_inputs" {
  name        = "AWSManagedRulesKnownBadInputsRuleSet"
  priority    = 4
  web_acl_arn = aws_wafv2_web_acl.this.arn

  override_action {
    none {}
  }

  statement {
    managed_rule_group_statement {
      name        = "AWSManagedRulesKnownBadInputsRuleSet"
      vendor_name = "AWS"
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.name_prefix}-known-bad-inputs"
    sampled_requests_enabled   = true
  }
}
