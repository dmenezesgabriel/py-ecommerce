output "backend_state_bucket_name" {
  value = aws_s3_bucket.terraform_state.bucket
}

output "backend_state_dynamo_lock_table" {
  value = aws_dynamodb_table.terraform_state.name
}

output "backend_state_kms_key_alias_name" {
  value = aws_kms_alias.key_alias.name
}
