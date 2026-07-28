package main

import rego.v1

# 1. Prevent the use of 'latest' tag
deny contains msg if {
  instruction := input[_]
  instruction.Cmd == "from"
  image := instruction.Value[0]

  endswith(image, ":latest")

  msg := sprintf("Security Risk: Base image '%v' uses the ':latest' tag. Pin a specific version.", [image])
}

# 2. Enforce lightweight images (slim or alpine)
deny contains msg if {
  instruction := input[_]
  instruction.Cmd == "from"
  image := instruction.Value[0]

  image != "scratch"
  not contains(lower(image), "slim")
  not contains(lower(image), "alpine")

  msg := sprintf("Optimization Risk: Base image '%v' is not a lightweight variant. Use '-slim' or 'alpine'.", [image])
}

# 3. Enforce non-root USER presence
deny contains msg if {
  user_instructions := [u | u := input[_]; u.Cmd == "user"]
  count(user_instructions) == 0

  msg := "Security Risk: No USER instruction found. The container will run as root by default."
}

# 4. Prevent explicit root USER
deny contains msg if {
  user_instructions := [u | u := input[_]; u.Cmd == "user"]
  count(user_instructions) > 0

  last_user := user_instructions[count(user_instructions) - 1].Value[0]
  lower(last_user) == "root"

  msg := "Security Risk: Container must not end with 'root' user. The final USER instruction must drop privileges."
}

# 5. Enforce Multi-Stage Builds
deny contains msg if {
  from_instructions := [f | f := input[_]; f.Cmd == "from"]
  count(from_instructions) < 2

  msg := "Optimization Risk: Single-stage build detected. Use Multi-Stage building (multiple FROM statements) to reduce final image size."
}
