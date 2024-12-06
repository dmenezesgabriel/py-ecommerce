variable "region" {
  type = string
}

variable "bucket_name" {
  type = string
}

variable "dynamodb_table_name" {
  type = string
}


variable "kms_alias_name" {
  type = string
}


# "${var.project_name}-${data.aws_caller_identity.current.account_id}"
# "alias/${var.project_name}-${data.aws_caller_identity.current.account_id}-backend-bucket"
