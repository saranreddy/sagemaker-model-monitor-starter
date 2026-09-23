variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix for resource naming"
  type        = string
  default     = "sagemaker-model-monitor"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for Model Monitor artifacts (defaults to auto-generated name)"
  type        = string
  default     = ""
}
