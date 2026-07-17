# Enterprise Policy-as-Code (OPA/Conftest)

This directory acts as the central nervous system for our DevSecOps pipeline. We utilize the Open Policy Agent (OPA) and Rego to enforce **Policy-as-Code** across the entire application lifecycle—from how a container is built (Docker), to how it is orchestrated (Kubernetes), to the physical cloud infrastructure it runs on (AWS).

## Why Policy-as-Code?
Manual code reviews are slow and error-prone. By defining our Security, FinOps, and Architectural standards as code, we create an automated "Golden Path." If a developer violates these standards, the CI/CD pipeline immediately catches the flaw and prevents the deployment, ensuring that our production environment remains secure, optimized, and cost-efficient.

---

## 1. Cloud Infrastructure Policies (AWS / Terraform)
Located in `aws_rules.rego`. These policies strictly control our cloud footprint, heavily focusing on **FinOps** and cost-efficiency.

* **Mandatory Spot & Graviton Instances:** EKS Node Groups are strictly limited to `t4g.medium` and `t4g.small` instance types, and must use `SPOT` capacity.
  * *The "Why":* AWS Graviton (t4g) provides up to 40% better price-performance over x86. Forcing SPOT instances ensures we pay a fraction of on-demand prices for our underlying compute.
* **Strict Tagging Enforcement:** All VPCs (and core infrastructure) must carry an `Environment` tag.
  * *The "Why":* Without strict tagging, granular cloud cost allocation is impossible. This ensures the FinOps dashboard can accurately track spending per environment.

---

## 2. Containerization Policies (Docker)
Located in `docker_rules.rego`. These rules enforce strict image optimization and least-privilege principles at the build phase.

* **Multi-Stage Builds & Lightweight Images:** Single-stage builds are rejected. All base images must be lightweight variants (`alpine` or `slim`), with exceptions for specific infrastructure tools (e.g., Jenkins).
  * *The "Why":* Multi-stage builds and slim base images drastically reduce the attack surface by eliminating unnecessary OS packages. They also accelerate pipeline build times and reduce ECR storage costs.
* **Least Privilege (Non-Root User):** Containers cannot run as root. A `USER` instruction must exist, and the final instruction cannot switch back to `root`.
  * *The "Why":* If a vulnerability is exploited within the application, running as a non-root user prevents the attacker from easily escalating privileges to the underlying worker node.
* **No Immutable Tags:** Using `:latest` as a base image is blocked.
  * *The "Why":* Upstream `:latest` images can change without warning, breaking build idempotency and introducing supply-chain security risks.

---

## 3. Orchestration Policies (Kubernetes)
Located in `k8s_rules.rego`. These rules govern how applications behave once deployed into the EKS cluster.

* **Resource Requests Required (Limits Omitted):** All containers must define resource `requests`.
  * *The "Why":* Requests are critical for the Kubernetes scheduler. However, we intentionally **do not enforce CPU limits**. Setting CPU limits often leads to CFS (Completely Fair Scheduler) quota throttling, artificially degrading app latency even when the node has idle CPU cycles.
* **No Privileged Pods:** Containers cannot run with `securityContext.privileged == true`.
  * *The "Why":* Privileged containers bypass namespace isolation. A compromised privileged pod equals a compromised Kubernetes cluster.
* **Deployment Idempotency & Tagging:** Kubernetes deployments cannot use `:latest` image tags and must include mandatory `env` labels.
  * *The "Why":* Guarantees that rollbacks are predictable and enables cost tracking down to the specific microservice.

---

## Local Validation (Developer Guide)

You can evaluate your code against these policies locally without waiting for CI/CD feedback. Ensure [Conftest](https://www.conftest.dev/) is installed.

**To test Dockerfiles:**
```bash
conftest test -p policy/docker_rules.rego Dockerfile
```

**To test K8s Helm Charts:**
```bash
helm template sentinel infrastructure/helm/sentinel/ | conftest test -p policy/k8s_rules.rego -
```

**To test Terraform:**
```bash
conftest test -p policy/aws_rules.rego infrastructure/terraform/
```
