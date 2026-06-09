resource "aws_eks_cluster" "sentinel_eks" {
  name     = "sentinel-production-cluster"
  role_arn = "arn:aws:iam::123456789012:role/MockEKSRole"

  vpc_config {
    subnet_ids = [aws_subnet.public_1.id]
  }
}

resource "aws_eks_node_group" "sentinel_nodes" {
  cluster_name    = aws_eks_cluster.sentinel_eks.name
  node_group_name = "sentinel-spot-nodes"
  node_role_arn   = "arn:aws:iam::123456789012:role/MockNodeRole"
  subnet_ids      = [aws_subnet.public_1.id]

  ami_type       = "AL2_ARM_64"
  instance_types = ["m6g.large"]
  capacity_type  = "SPOT" # Faturayı asıl ezecek olan satır

  scaling_config {
    desired_size = 3
    max_size     = 5
    min_size     = 2
  }
}
