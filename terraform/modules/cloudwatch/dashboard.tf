resource "aws_cloudwatch_dashboard" "this" {
  dashboard_name = "${var.name_prefix}-overview"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 8
        properties = {
          title   = "Lambda Errors"
          region  = data.aws_region.current.region
          metrics = local.lambda_error_metrics
          stat    = "Sum"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 8
        properties = {
          title   = "Lambda Duration (Max)"
          region  = data.aws_region.current.region
          metrics = local.lambda_duration_metrics
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 8
        properties = {
          title  = "API Gateway 5xx"
          region = data.aws_region.current.region
          metrics = [
            ["AWS/ApiGateway", "5xx", "ApiId", var.api_gateway_id]
          ]
          stat   = "Sum"
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 8
        properties = {
          title  = "API Gateway Latency (Max)"
          region = data.aws_region.current.region
          metrics = [
            ["AWS/ApiGateway", "Latency", "ApiId", var.api_gateway_id]
          ]
          stat   = "Maximum"
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 12
        height = 8
        properties = {
          title  = "DLQ Depth"
          region = data.aws_region.current.region
          metrics = [
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", var.dlq_name]
          ]
          stat   = "Maximum"
          period = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 12
        width  = 12
        height = 8
        properties = {
          title  = "DLQ Oldest Message Age"
          region = data.aws_region.current.region
          metrics = [
            ["AWS/SQS", "ApproximateAgeOfOldestMessage", "QueueName", var.dlq_name]
          ]
          stat   = "Maximum"
          period = 300
        }
      }
    ]
  })
}
