resource "aws_cloudwatch_metric_alarm" "dlq_depth" {
  alarm_name        = "${var.name_prefix}-dlq-depth"
  alarm_description = "Triggers when messages are present in the dead-letter queue"

  namespace   = "AWS/SQS"
  metric_name = "ApproximateNumberOfMessagesVisible"
  dimensions = {
    QueueName = var.dlq_name
  }

  period              = 300
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  statistic           = "Maximum"
  comparison_operator = "GreaterThanThreshold"
  threshold           = 0
  treat_missing_data  = "notBreaching"

  alarm_actions = [var.sns_topic_arn]
}

resource "aws_cloudwatch_metric_alarm" "dlq_oldest_message_age" {
  alarm_name        = "${var.name_prefix}-dlq-oldest-message-age"
  alarm_description = "Triggers when a message has been stuck in the dead-letter queue too long"

  namespace   = "AWS/SQS"
  metric_name = "ApproximateAgeOfOldestMessage"
  dimensions = {
    QueueName = var.dlq_name
  }

  period              = 300
  evaluation_periods  = 1
  datapoints_to_alarm = 1
  statistic           = "Maximum"
  comparison_operator = "GreaterThanThreshold"
  threshold           = 3600 # 1 hour
  treat_missing_data  = "notBreaching"

  alarm_actions = [var.sns_topic_arn]
}
