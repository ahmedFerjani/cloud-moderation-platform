resource "aws_sns_topic" "this" {
  name = lower(
    "${var.project_name}-${var.environment}-${var.purpose}"
  )
}
