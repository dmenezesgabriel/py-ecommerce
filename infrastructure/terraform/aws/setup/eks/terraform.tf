terraform {

  required_version = "~> 1.0"

  # --- Assure that the bucket and dynamo db table are created at backend dir
  backend "s3" {
    bucket         = "postech-challenge-3-293351734410"
    key            = "state/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    kms_key_id     = "alias/postech-challenge-3-293351734410-backend-bucket"
    dynamodb_table = "postech-challenge-3-293351734410"
  }
  # --- Assure that the bucket and dynamo db table are created at backend dir
  required_providers {

    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
