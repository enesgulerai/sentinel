package main

import rego.v1

# 1. Allowed Instance Types Rule
deny contains msg if {
  node_group := input.resource.aws_eks_node_group[_][_]
  instance_type := node_group.instance_types[_]

  allowed_types := {"t4g.medium", "t4g.small"}
  not allowed_types[instance_type]

  msg := sprintf("FinOps Violation: Instance type '%v' is not allowed. Only t4g.medium and t4g.small are permitted.", [instance_type])
}

# 2. Spot Instance Rule
deny contains msg if {
  node_group := input.resource.aws_eks_node_group[_][_]

  node_group.capacity_type != "SPOT"

  msg := "FinOps Violation: EKS Node Group capacity_type must be set to 'SPOT' for cost optimization."
}

# 3. Environment Tag Rule
deny contains msg if {
  vpc := input.resource.aws_vpc[_][_]

  not vpc.tags["Environment"]

  msg := "Standardization Violation: All VPCs must have an 'Environment' tag defined."
}
