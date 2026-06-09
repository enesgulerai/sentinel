resource "aws_vpc" "sentinel_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "sentinel-production-vpc" }
}

resource "aws_internet_gateway" "sentinel_igw" {
  vpc_id = aws_vpc.sentinel_vpc.id
  tags = { Name = "sentinel-igw" }
}

resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.sentinel_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true # OCI'daki assign_public_ip mantığı
}
