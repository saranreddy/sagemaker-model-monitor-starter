output "sagemaker_role_arn" {
  description = "ARN of the SageMaker execution role (use in config.yaml)"
  value       = aws_iam_role.sagemaker_execution.arn
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for Model Monitor artifacts (use in config.yaml)"
  value       = aws_s3_bucket.model_monitor.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.model_monitor.arn
}

output "aws_region" {
  description = "AWS region where resources were created"
  value       = data.aws_region.current.name
}

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}
