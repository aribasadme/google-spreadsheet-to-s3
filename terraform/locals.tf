locals {
  env          = lower(var.env)
  service_name = var.plan_name

  tf_common_tags = {
    Environment            = local.env
    Product                = local.service_name
    Terraform              = "true"
    "Terraform Repository" = var.repository
  }
}
