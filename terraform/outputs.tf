output "content_bucket_name" {
  value = module.content_bucket.bucket_name
}

output "content_bucket_arn" {
  value = module.content_bucket.bucket_arn
}

output "moderation_table_name" {
  value = module.moderation_table.table_name
}

output "moderation_table_arn" {
  value = module.moderation_table.table_arn
}
