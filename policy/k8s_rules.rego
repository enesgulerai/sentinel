package main

import rego.v1

# 1. RESOURCE MANAGEMENT

# Rule 1.1: All containers must have 'requests' defined for accurate scheduling.
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  not container.resources.requests

  msg := sprintf("Reliability Risk: Container '%v' in Deployment '%v' is missing resource 'requests'.", [container.name, input.metadata.name])
}

# Rule 1.2: CPU 'limits' are strictly forbidden to prevent CFS quota throttling.
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  container.resources.limits.cpu

  msg := sprintf("Performance Risk: Container '%v' in Deployment '%v' defines CPU limits. This is forbidden to prevent CFS throttling.", [container.name, input.metadata.name])
}

# 2. POD SECURITY

# Rule 2.1: Privileged containers are strictly forbidden.
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  container.securityContext.privileged == true

  msg := sprintf("Security Risk: Container '%v' in Deployment '%v' is running as privileged. This violates cluster isolation.", [container.name, input.metadata.name])
}

# 3. SUPPLY CHAIN & FINOPS

# Rule 3.1: The ':latest' image tag is forbidden to ensure deployment idempotency.
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  endswith(container.image, ":latest")

  msg := sprintf("Deployment Risk: Container '%v' in Deployment '%v' uses the ':latest' tag. Explicit versioning is required.", [container.name, input.metadata.name])
}

# Rule 3.2: Standardized FinOps labels must be present on the Pod template.
mandatory_labels := {"environment", "owner", "project"}

deny contains msg if {
  input.kind == "Deployment"
  label := mandatory_labels[_]

  # We check the pod template metadata, because this is what generates the actual pods
  not input.spec.template.metadata.labels[label]

  msg := sprintf("FinOps Risk: Deployment '%v' is missing the mandatory label '%v' in its pod template.", [input.metadata.name, label])
}
