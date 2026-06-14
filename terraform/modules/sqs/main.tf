resource "aws_sqs_queue" "dlq" {
  name = lower(
    "${var.project_name}-${var.environment}-dlq"
  )

  message_retention_seconds = var.message_retention_seconds_dlq_queue
}

resource "aws_sqs_queue" "main" {
  name = lower(
    "${var.project_name}-${var.environment}-main-queue"
  )

  message_retention_seconds  = var.message_retention_seconds_main_queue
  visibility_timeout_seconds = var.visibility_timeout_seconds

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.max_receive_count
  })
}
