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
  tags = { Name = "sentinel-igw" }
}

# Architectural Decision Record (ADR): Public vs Private Subnets
# In a strict production environment, worker nodes should reside in a Private Subnet
# and route outbound traffic through a NAT Gateway for security purposes.
# However, AWS NAT Gateways incur a baseline cost of ~$32/month plus data processing fees.
# For this specific deployment, we are intentionally placing nodes in a Public Subnet
# to prioritize FinOps and cost optimization over strict network isolation.

# AZ-A Subnet (Primary subnet where worker nodes will run)
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.sentinel_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true
}

# AZ-B Subnet (Required solely to satisfy EKS Control Plane multi-AZ requirement)
resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.sentinel_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true
}
