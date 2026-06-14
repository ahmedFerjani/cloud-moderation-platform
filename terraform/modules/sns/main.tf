resource "aws_sns_topic" "this" {
  name = lower(
    "${var.project_name}-${var.environment}-${var.purpose}"
  )
}

resource "aws_sns_topic_subscription" "email" {
  for_each = toset(var.notification_emails)

  topic_arn = aws_sns_topic.this.arn
  protocol  = "email"
  endpoint  = each.value
}
