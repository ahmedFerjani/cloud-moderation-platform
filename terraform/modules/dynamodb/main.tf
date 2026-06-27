resource "aws_dynamodb_table" "this" {
  name         = lower("${var.name_prefix}-${var.purpose}")
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "imageId"

  attribute {
    name = "imageId"
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
  index_name = "imageHash-index"

  projection {
    projection_type = "ALL"
  }

  key_schema {
    attribute_name = "imageHash"
    attribute_type = "S"
    key_type       = "HASH"
  }
}
