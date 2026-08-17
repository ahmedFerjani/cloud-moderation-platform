resource "aws_dynamodb_table" "this" {
  name         = lower("${var.name_prefix}-results")
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "image_id"

  attribute {
    name = "image_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  ttl {
    attribute_name = "expiresAt"
    enabled        = true
  }
}

resource "aws_dynamodb_global_secondary_index" "this" {
  table_name = aws_dynamodb_table.this.name
  index_name = "image_hash_index"

  key_schema {
    attribute_name = "image_hash"
    attribute_type = "S"
    key_type       = "HASH"
  }

  projection {
    projection_type = "ALL"
  }
}
