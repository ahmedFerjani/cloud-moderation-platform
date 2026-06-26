data "aws_ssm_parameter" "google_client_id" {
  name = "/${var.project_name}/${var.environment}/google/client_id"
  with_decryption = true
}

data "aws_ssm_parameter" "google_client_secret" {
  name            = "/${var.project_name}/${var.environment}/google/client_secret"
  with_decryption = true
}
