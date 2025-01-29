resource "aws_s3_bucket" "bucket" {
  bucket = var.bucket_name

  tags = local.tf_common_tags
}
