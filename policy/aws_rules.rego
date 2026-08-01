package main

import rego.v1

# 1. FinOps & Governance

# Rule 1.1: Allow only specific Graviton (ARM) instance types.
deny contains msg if {
  node_group := input.resource.aws_eks_node_group[_][_]
  instance_type := node_group.instance_types[_]
  allowed_types := {"t4g.medium", "t4g.small"}

  not allowed_types[instance_type]
  msg := sprintf("FinOps Violation: EKS Node Group instance type '%v' is not allowed. Only %v are permitted (Graviton optimized).", [instance_type, allowed_types])
}

# Rule 1.2: EKS Node Group capacity must strictly be SPOT.
deny contains msg if {
  node_group := input.resource.aws_eks_node_group[_][_]
  node_group.capacity_type != "SPOT"
  msg := "FinOps Violation: EKS Node Group 'capacity_type' must be 'SPOT' to reduce compute costs."
}

# Rule 1.3: Deprecate legacy gp2 disks, enforce gp3.
deny contains msg if {
  volume := input.resource.aws_ebs_volume[_][_]
  volume.type == "gp2"
  msg := "FinOps Violation: EBS volume type 'gp2' is deprecated in this project. Use the cheaper and faster 'gp3'."
}

# Rule 1.4: Mandatory Enterprise Tagging. Extend tag checks beyond VPC to S3 and EKS clusters.
mandatory_tags := {"Environment", "Owner", "Project"}

deny contains msg if {
  resource_types := {"aws_vpc", "aws_eks_cluster", "aws_s3_bucket"}
  resource_type := resource_types[_]
  resource := input.resource[resource_type][_][_]

  tag := mandatory_tags[_]
  not has_tag(resource, tag)

  msg := sprintf("Governance Violation: Resource '%v' is missing the mandatory tag: '%v'.", [resource_type, tag])
}

# Helper function to parse tags whether Conftest reads them as an Object or an Array of Objects
has_tag(resource, tag) if {
  val := resource.tags[tag]
  val != ""
}

has_tag(resource, tag) if {
  val := resource.tags[_][tag]
  val != ""
}

# 2. Network Security

# Rule 2.1: Prohibit exposing dangerous ports (SSH, RDP, DB) to the internet (0.0.0.0/0).
dangerous_ports := {22, 3389, 3306, 5432}

deny contains msg if {
  sg_rule := input.resource.aws_security_group_rule[_][_]
  sg_rule.type == "ingress"
  sg_rule.cidr_blocks[_] == "0.0.0.0/0"

  port := dangerous_ports[_]
  sg_rule.from_port <= port
  sg_rule.to_port >= port

  msg := sprintf("Security Violation: Security Group rule allows internet (0.0.0.0/0) access to dangerous port %v.", [port])
}

# 3. Data Security

# Rule 3.1: EBS volumes must be encrypted by default.
deny contains msg if {
  volume := input.resource.aws_ebs_volume[_][_]
  not volume.encrypted
  msg := "Security Violation: EBS volumes must have 'encrypted = true'."
}

# Rule 3.2: S3 Buckets must never be publicly readable (public-read ACL is forbidden).
deny contains msg if {
  bucket := input.resource.aws_s3_bucket[_][_]
  bucket.acl == "public-read"
  msg := "Security Violation: S3 Bucket ACL cannot be 'public-read'. Data must remain private."
}

# 4. IAM Least Privilege

# Rule 4.1: Action = "*" or Resource = "*" is forbidden in IAM Policies (No Full Admin).
# Terraform stores IAM policies as JSON strings, so we parse them using Regex.
deny contains msg if {
  policy := input.resource.aws_iam_policy[_][_]
  regex.match(`"Action"\s*:\s*"\*"`, policy.policy)
  msg := "Security Violation: IAM Policy contains Action = '*'. Principle of Least Privilege must be enforced."
}

deny contains msg if {
  policy := input.resource.aws_iam_policy[_][_]
  regex.match(`"Resource"\s*:\s*"\*"`, policy.policy)
  msg := "Security Violation: IAM Policy contains Resource = '*'. Principle of Least Privilege must be enforced."
}
