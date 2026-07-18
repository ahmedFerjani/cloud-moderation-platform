locals {
  lambda_error_metrics = [
    for name, fn in var.lambdas : ["AWS/Lambda", "Errors", "FunctionName", fn.function_name, { label = name }]
  ]

  lambda_duration_metrics = [
    for name, fn in var.lambdas : ["AWS/Lambda", "Duration", "FunctionName", fn.function_name, { label = name, stat = "Maximum" }]
  ]
}
