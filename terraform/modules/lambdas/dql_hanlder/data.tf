data "aws_iam_policy_document" "dlq_handler_lambda_policy" {
  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [var.dlq_arn]
  }

  statement {
    actions   = ["dynamodb:PutItem"]
    resources = [var.moderation_table_arn]
  }

  statement {
    actions   = ["sns:Publish"]
    resources = [var.failure_topic_arn]
  }
}
