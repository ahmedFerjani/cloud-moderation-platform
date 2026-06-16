resource "aws_iam_role" "this" {
  name = lower("${var.project_name}-${var.environment}-orchestrator-lambda-role")
  assume_role_policy = var.lambda_assume_role_json
}

resource "aws_iam_role_policy_attachment" "basic" {
  role       = aws_iam_role.this.name
  policy_arn = var.lambda_basic_execution_arn
}

resource "aws_iam_role_policy" "orchestrator_lambda_policy" {
  name = lower("${var.project_name}-${var.environment}-orchestrator-lambda-policy")
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.orchestrator_lambda_policy.json
}
