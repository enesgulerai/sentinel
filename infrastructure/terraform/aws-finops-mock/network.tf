resource "aws_vpc" "sentinel_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "sentinel-production-vpc"
    Environment = "Production"
  }
}

resource "aws_internet_gateway" "sentinel_igw" {
  vpc_id = aws_vpc.sentinel_vpc.id
  tags   = { Name = "sentinel-igw" }
}

# Architectural Decision Record (ADR): Public vs Private Subnets
# In a strict production environment, worker nodes should reside in a Private Subnet
# and route outbound traffic through a NAT Gateway for security purposes.
# However, AWS NAT Gateways incur a baseline cost of ~$32/month plus data processing fees.
# For this specific deployment, we are intentionally placing nodes in a Public Subnet
# to prioritize FinOps and cost optimization over strict network isolation.

# AZ-A Subnet (Primary subnet where worker nodes will run)
resource "aws_subnet" "public_1" {
  # checkov:skip=CKV_AWS_130: Node instances require public IPs without a costly NAT Gateway (FinOps).
  vpc_id                  = aws_vpc.sentinel_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
}

# AZ-B Subnet (Required solely to satisfy EKS Control Plane multi-AZ requirement)
resource "aws_subnet" "public_2" {
  # checkov:skip=CKV_AWS_130: Node instances require public IPs without a costly NAT Gateway (FinOps).
  vpc_id                  = aws_vpc.sentinel_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
}

# Lock down the default security group (CKV2_AWS_12)
resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.sentinel_vpc.id
}

# Enable VPC Flow Logs (CKV2_AWS_11)
resource "aws_flow_log" "sentinel_vpc_flow_log" {
  iam_role_arn    = aws_iam_role.vpc_flow_log_role.arn
  log_destination = aws_cloudwatch_log_group.sentinel_vpc_log_group.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.sentinel_vpc.id
}

# CloudWatch Log Group for Flow Logs
resource "aws_cloudwatch_log_group" "sentinel_vpc_log_group" {
  # checkov:skip=CKV_AWS_158: KMS encryption skipped for flow logs to optimize costs.
  name              = "/aws/vpc/sentinel-production-vpc/flow-logs"
  retention_in_days = 365 # CKV_AWS_338: Retain logs for at least 1 year
}

# IAM Role to allow VPC to write Flow Logs to CloudWatch
resource "aws_iam_role" "vpc_flow_log_role" {
  name = "sentinel-vpc-flow-log-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "vpc_flow_log_policy" {
  name = "sentinel-vpc-flow-log-policy"
  role = aws_iam_role.vpc_flow_log_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
        ]
        Effect = "Allow"
        # CKV_AWS_355 & 290: Strict restriction instead of "*"
        Resource = "${aws_cloudwatch_log_group.sentinel_vpc_log_group.arn}:*"
      }
    ]
  })
}
