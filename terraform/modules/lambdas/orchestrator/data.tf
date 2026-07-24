data "aws_iam_policy_document" "orchestrator_lambda_policy" {
  statement {
    actions   = ["rekognition:DetectModerationLabels"]
    resources = ["*"]
  }

  statement {
    actions   = ["textract:DetectDocumentText"]
    resources = ["*"]
  }

  statement {
    actions = [
      "comprehend:DetectDominantLanguage",
      "comprehend:DetectSentiment",
      "comprehend:DetectPiiEntities",
      "comprehend:DetectToxicContent"
    ]
    resources = ["*"]
  }

  statement {
    actions   = ["s3:GetObject"]
    resources = ["${var.content_bucket_arn}/uploads/*"]
  }

  statement {
    actions   = ["dynamodb:PutItem"]
    resources = [var.moderation_table_arn]
  }

  statement {
    actions   = ["dynamodb:Query"]
    resources = ["${var.moderation_table_arn}/index/imageHash-index"]
  }

  statement {
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [var.main_queue_arn]
  }

  statement {
    actions   = ["dynamodb:Query"]
    resources = ["${var.connections_table_arn}/index/userId-index"]
  }

  statement {
    actions   = ["execute-api:ManageConnections"]
    resources = ["${var.websocket_execution_arn}/*/POST/@connections/*"]
  }
}
