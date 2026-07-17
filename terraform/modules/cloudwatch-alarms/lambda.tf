resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  for_each = var.lambda_function_names

  alarm_name        = "${var.name_prefix}-${each.key}-errors"
  alarm_description = "Triggers when ${each.key} has any errors in a 5-minute window"

  namespace   = "AWS/Lambda"
  metric_name = "Errors"
  dimensions = {
    FunctionName = each.value
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

resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  for_each = var.lambda_function_names

  alarm_name        = "${var.name_prefix}-${each.key}-throttles"
  alarm_description = "Triggers when ${each.key} is throttled in a 5-minute window"

  namespace   = "AWS/Lambda"
  metric_name = "Throttles"
  dimensions = {
    FunctionName = each.value
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
