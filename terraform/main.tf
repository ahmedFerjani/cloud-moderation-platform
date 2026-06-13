module "content_bucket" {
  source = "./modules/s3"

  account_id   = local.account_id
  environment  = var.environment
  project_name = var.project_name
  purpose      = "uploads"
  region       = local.region
}
