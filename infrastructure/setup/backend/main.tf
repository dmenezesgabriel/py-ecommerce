terraform {

  required_version = "~> 1.0"

  required_providers {

    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

module "backend" {
  source              = "../modules/backend"
  region              = var.region
  bucket_name         = "${var.project_name}-${data.aws_caller_identity.current.account_id}"
  dynamodb_table_name = "${var.project_name}-${data.aws_caller_identity.current.account_id}"
  kms_alias_name      = "alias/${var.project_name}-${data.aws_caller_identity.current.account_id}-backend-bucket"
}
