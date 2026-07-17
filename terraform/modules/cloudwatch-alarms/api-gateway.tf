resource "aws_cloudwatch_metric_alarm" "api_5xx" {
  alarm_name        = "${var.name_prefix}-api-gateway-5xx"
  alarm_description = "Triggers when API Gateway returns 5xx errors"

  namespace   = "AWS/ApiGateway"
  metric_name = "5xx"
  dimensions = {
    ApiId = var.api_gateway_id
  }

  period              = 300
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  statistic           = "Sum"
  comparison_operator = "GreaterThanThreshold"
  threshold           = 0
  treat_missing_data  = "notBreaching"

  alarm_actions = [var.sns_topic_arn]
}

resource "aws_cloudwatch_metric_alarm" "api_latency" {
  alarm_name        = "${var.name_prefix}-api-gateway-latency"
  alarm_description = "Triggers when API Gateway maximum latency exceeds 3 seconds"

  namespace   = "AWS/ApiGateway"
  metric_name = "Latency"
  dimensions = {
    ApiId = var.api_gateway_id
  }

  period              = 300
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  statistic  = "Maximum"
  comparison_operator = "GreaterThanThreshold"
  threshold           = 3000 # 3 seconds
  treat_missing_data  = "notBreaching"

  alarm_actions = [var.sns_topic_arn]
}
