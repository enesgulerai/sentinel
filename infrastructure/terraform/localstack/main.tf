terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "environment" {
  description = "The deployment environment"
  type        = string
  default     = "local"
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
    s3 = "http://localhost:4566"
  }

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "Sentinel"
      ManagedBy   = "Terraform"
    }
  }
}

resource "aws_s3_bucket" "sentinel_audit_logs" {
  bucket = "sentinel-audit-logs-local"

  tags = {
    Environment = "dev"
    Owner       = "sentinel-team"
    Project     = "sentinel"
  }
}

resource "aws_s3_bucket_versioning" "sentinel_audit_logs_versioning" {
  bucket = aws_s3_bucket.sentinel_audit_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

output "s3_bucket_name" {
  value = aws_s3_bucket.sentinel_audit_logs.bucket
}
