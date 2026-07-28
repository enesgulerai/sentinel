# KMS Key for EKS Secrets Encryption (CKV_AWS_58)
resource "aws_kms_key" "eks_secrets" {
  description             = "EKS Secret Encryption Key"
  enable_key_rotation     = true
  deletion_window_in_days = 7

  # CKV2_AWS_64: Explicitly define the KMS key policy
  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "key-default-1"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::123456789012:root"
        }
        Action   = "kms:*"
        Resource = "*"
      }
    ]
  })
}

# EKS Node Launch Template
resource "aws_launch_template" "sentinel_nodes_lt" {
  name = "sentinel-spot-nodes-lt"

  instance_market_options {
    market_type = "spot"
  }

  block_device_mappings {
    device_name = "/dev/xvda"

    ebs {
      volume_size = 20
      volume_type = "gp3"
    }
  }

  # Enforce IMDSv2 for security (CKV_AWS_79)
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }
}

# EKS Cluster (Control Plane)
resource "aws_eks_cluster" "sentinel_eks" {
  # checkov:skip=CKV_AWS_39: Public endpoint is required for CI/CD deployments.
  name     = "sentinel-production-cluster"
  role_arn = "arn:aws:iam::123456789012:role/MockEKSRole"

  # Enable Control Plane Logging (CKV_AWS_37)
  enabled_cluster_log_types = ["api", "audit", "authenticator", "controllerManager", "scheduler"]

  vpc_config {
    subnet_ids = [aws_subnet.public_1.id, aws_subnet.public_2.id]

    # Restrict Public Endpoint (CKV_AWS_38)
    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = ["198.51.100.10/32"]
  }

  encryption_config {
    provider {
      key_arn = aws_kms_key.eks_secrets.arn
    }
    resources = ["secrets"]
  }

  tags = {
    Environment = "dev"
    Owner       = "sentinel-team"
    Project     = "sentinel"
  }
}

# EKS Node Group (Worker Nodes)
resource "aws_eks_node_group" "sentinel_nodes" {
  cluster_name    = aws_eks_cluster.sentinel_eks.name
  node_group_name = "sentinel-spot-nodes"
  node_role_arn   = "arn:aws:iam::123456789012:role/MockNodeRole"

  # FinOps Optimization: Nodes are restricted to a single AZ (public_1)
  # to completely avoid cross-AZ data transfer charges.
  subnet_ids = [aws_subnet.public_1.id]

  ami_type       = "AL2_ARM_64"
  instance_types = ["t4g.medium"]
  capacity_type  = "SPOT"

  launch_template {
    name    = aws_launch_template.sentinel_nodes_lt.name
    version = aws_launch_template.sentinel_nodes_lt.latest_version
  }

  scaling_config {
    desired_size = 2
    max_size     = 5
    min_size     = 1
  }
}
