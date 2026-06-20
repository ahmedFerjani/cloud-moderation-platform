# Allow S3 to send messages to the main SQS queue
resource "aws_sqs_queue_policy" "this" {
  queue_url = var.main_queue_url

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "s3.amazonaws.com"
      }
      Action   = "SQS:SendMessage"
      Resource = var.main_queue_arn
      Condition = {
        ArnLike = {
          "aws:SourceArn" = var.bucket_arn
        }
      }
    }]
  })
}


resource "aws_s3_bucket_notification" "this" {
  bucket = var.bucket_id

  queue {
    queue_arn     = var.main_queue_arn
    events        = ["s3:ObjectCreated:*"]
    filter_prefix = "uploads/"
  }

  depends_on = [aws_sqs_queue_policy.this]
}

resource "aws_lambda_event_source_mapping" "orchestrator" {
  event_source_arn = var.main_queue_arn
  function_name    = var.orchestrator_lambda_arn
}

resource "aws_lambda_event_source_mapping" "dlq_handler" {
  event_source_arn = var.dlq_arn
  function_name    = var.dlq_handler_lambda_arn
}