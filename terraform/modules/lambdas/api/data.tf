data "aws_iam_policy_document" "api_lambda_policy" {
  statement {
    actions   = ["s3:PutObject"]
    resources = ["${var.content_bucket_arn}/uploads/*"]
  }

  statement {
    actions = [
      "dynamodb:GetItem",
      "dynamodb:Scan"
    ]

    resources = [var.moderation_results_table_arn]
  }
}
