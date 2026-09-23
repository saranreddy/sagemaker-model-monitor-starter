resource "aws_s3_bucket" "model_monitor" {
  bucket = var.s3_bucket_name != "" ? var.s3_bucket_name : "${var.project_name}-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "Model Monitor Artifacts"
    Description = "Stores baseline data, captured inference data, and monitoring reports"
  }
}

resource "aws_s3_bucket_versioning" "model_monitor" {
  bucket = aws_s3_bucket.model_monitor.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "model_monitor" {
  bucket = aws_s3_bucket.model_monitor.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "model_monitor" {
  bucket = aws_s3_bucket.model_monitor.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
