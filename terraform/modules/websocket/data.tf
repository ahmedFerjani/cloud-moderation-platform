data "aws_iam_policy_document" "connect" {
  statement {
    actions   = ["dynamodb:PutItem"]
    resources = [aws_dynamodb_table.this.arn]
  }
}

data "aws_iam_policy_document" "disconnect" {
  statement {
    actions   = ["dynamodb:DeleteItem"]
    resources = [aws_dynamodb_table.this.arn]
  }
}
