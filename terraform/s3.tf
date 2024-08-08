import {
  to = aws_s3_bucket.bucket
  id = var.bucket_name
}

resource "aws_s3_bucket" "bucket" {
  bucket = var.bucket_name

  tags = {
    Environment            = local.env
    Product                = local.service_name
    Terraform              = "true"
    "Terraform Repository" = var.repository
  }
}
