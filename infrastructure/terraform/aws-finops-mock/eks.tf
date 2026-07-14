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
}

# EKS Cluster (Control Plane)
resource "aws_eks_cluster" "sentinel_eks" {
  name     = "sentinel-production-cluster"
  role_arn = "arn:aws:iam::123456789012:role/MockEKSRole"

  vpc_config {
    # EKS API requires at least 2 subnets in different AZs to successfully provision.
    subnet_ids = [aws_subnet.public_1.id, aws_subnet.public_2.id]
  }
}

# EKS Node Group (Worker Nodes)
resource "aws_eks_node_group" "sentinel_nodes" {
  cluster_name    = aws_eks_cluster.sentinel_eks.name
  node_group_name = "sentinel-spot-nodes"
  node_role_arn   = "arn:aws:iam::123456789012:role/MockNodeRole"

  # FinOps Optimization: Nodes are restricted to a single AZ (public_1)
  # to completely avoid cross-AZ data transfer charges.
  subnet_ids      = [aws_subnet.public_1.id]

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
