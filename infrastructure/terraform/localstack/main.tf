terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  s3_use_path_style           = true

  endpoints {
    s3  = "http://localhost:4566"
    sqs = "http://localhost:4566"
    iam = "http://localhost:4566"
  }
}

# 1. S3 Bucket
resource "aws_s3_bucket" "sentinel_audit_logs" {
  bucket = "sentinel-audit-logs-local"
}

# 2. SQS Queue
resource "aws_sqs_queue" "sentinel_risk_queue" {
  name = "sentinel-risk-transactions-queue"
}


output "s3_bucket_name" {
  value = aws_s3_bucket.sentinel_audit_logs.bucket
}

output "sqs_queue_url" {
  value = aws_sqs_queue.sentinel_risk_queue.url
}
