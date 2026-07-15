package main

# 1. Enforce Resource Requests (Limits intentionally omitted to prevent CFS throttling)
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  # Check if resources.requests block is missing
  not container.resources.requests

  msg := sprintf("Reliability Risk: Container '%v' in Deployment '%v' must have resource 'requests' defined for proper scheduling.", [container.name, input.metadata.name])
}

# 2. Prevent Privileged Containers
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  container.securityContext.privileged == true

  msg := sprintf("Security Risk: Container '%v' in Deployment '%v' is running as privileged. This is strictly forbidden.", [container.name, input.metadata.name])
}

# 3. Prevent ':latest' Image Tags
deny contains msg if {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]

  endswith(container.image, ":latest")

  msg := sprintf("Deployment Risk: Container '%v' in Deployment '%v' uses the ':latest' tag. Use explicit version tags.", [container.name, input.metadata.name])
}

# 4. Enforce Mandatory Labels (e.g., 'env')
deny contains msg if {
  input.kind == "Deployment"

  not input.metadata.labels.env

  msg := sprintf("FinOps Risk: Deployment '%v' is missing the mandatory 'env' label in its metadata.", [input.metadata.name])
}
