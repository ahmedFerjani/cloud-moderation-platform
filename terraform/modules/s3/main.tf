resource "aws_s3_bucket" "this" {
  bucket        = lower("${var.name_prefix}-${var.purpose}-${var.region}-${var.account_id}")
  force_destroy = var.environment == "dev"
}

resource "aws_s3_bucket_ownership_controls" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket = aws_s3_bucket.this.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  rule {
    id     = "cleanup-old-objects"
    status = "Enabled"

    expiration {
      days = 30
    }
  }
}

resource "aws_s3_bucket_cors_configuration" "this" {
  bucket = aws_s3_bucket.this.id

  cors_rule {
    allowed_origins = var.frontend_origins

    allowed_methods = [
      "POST",
      "GET",
      "HEAD"
    ]

    allowed_headers = ["*"]

    expose_headers = [
      "ETag"
    ]

    max_age_seconds = 3000
  }
}
