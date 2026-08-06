<div align="left">

# Sentinel: Enterprise Real-Time Fraud & Anomaly Ingestion Engine
### Module: Enterprise Policy-as-Code (OPA/Conftest)

</div>

---

## Overview
This module acts as the central nervous system for the DevSecOps pipeline. We utilize the Open Policy Agent (OPA) and Rego to enforce **Policy-as-Code** across the entire application lifecycle—from container builds (Docker), to workload orchestration (Kubernetes), down to the physical cloud infrastructure (AWS). By defining Security, FinOps, and Architectural standards as code, we create an automated "Golden Path." Pipeline validations immediately catch flaws and prevent non-compliant deployments, ensuring the production environment remains secure, optimized, and cost-efficient.

## Core Policy Domains

### 1. Cloud Infrastructure (AWS / Terraform)
Located in `aws_rules.rego`. These policies strictly control the cloud footprint, enforcing FinOps, Network Security, Data Security, and IAM Least Privilege.
*   **FinOps & Governance:** EKS Node Groups are strictly limited to Graviton instances (`t4g.medium`, `t4g.small`) and must use `SPOT` capacity. Legacy `gp2` disks are deprecated in favor of `gp3` to maximize price-performance.
*   **Mandatory Enterprise Tagging:** All critical resources (VPC, EKS Clusters, S3 Buckets) must carry `Environment`, `Owner`, and `Project` tags to guarantee granular cost allocation and ownership tracking.
*   **Network Security:** Security Groups are prohibited from exposing administrative or database ports (e.g., 22, 3306, 5432) to the internet (`0.0.0.0/0`) to prevent brute-force attack vectors.
*   **Data Security:** EBS volumes must be encrypted by default (`encrypted = true`), and S3 buckets can never use a `public-read` ACL to ensure data-at-rest is always protected.
*   **IAM Least Privilege:** IAM Policies cannot contain `Action = "*"` or `Resource = "*"`. Restricting IAM scope strictly limits the blast radius of a compromised resource.

### 2. Containerization (Docker)
Located in `docker_rules.rego`. Enforces a zero-exception, enterprise-grade standard for all container images, focusing on supply chain security and size optimization.
*   **Strict Multi-Stage Builds:** Single-stage builds are completely forbidden. Every Dockerfile must use at least two `FROM` instructions to leave behind build tools and minimize the attack surface.
*   **Lightweight Base Images Only:** Base images must be a `slim`, `alpine`, or `scratch` variant to eliminate unnecessary OS packages and potential CVEs.
*   **No ':latest' Tags:** Pinning explicit version tags is mandatory to ensure absolute build reproducibility and pipeline stability.
*   **Enforced Non-Root User:** A `USER` instruction must be present, and the final user cannot be `root`, preventing attackers from easily escalating privileges to the underlying host or cluster.

### 3. Orchestration (Kubernetes)
Located in `k8s_rules.rego`. Governs how applications behave inside the EKS cluster, maximizing reliability, security, and FinOps visibility.
*   **Resource Management (CFS Protection):** All containers must define resource `requests` for accurate scheduling, but setting CPU `limits` is **strictly forbidden**. This prevents artificial Linux Kernel CFS quota throttling, allowing services to utilize idle compute.
*   **Pod Security & Isolation:** Containers cannot run with `securityContext.privileged == true`, preserving namespace isolation and protecting the worker nodes.
*   **Supply Chain & Enterprise FinOps:** Deployments cannot use the `:latest` image tag. Furthermore, all Pod templates must include mandatory enterprise labels (`environment`, `owner`, `project`) to integrate accurately with cluster cost-monitoring tools like Kubecost.

## Prerequisites
Ensure the following tools are present in your local environment for policy evaluation:
*   **[Conftest](https://www.conftest.dev/):** Utility for writing and executing tests against structured configuration data.
*   **[Helm]:** Required for rendering Kubernetes manifests before passing them to the validation engine.

## Local Validation & Usage
Evaluate your code against these policies locally to achieve rapid feedback before triggering CI/CD pipelines.

### 1. Validate Terraform (AWS Infrastructure)
```bash
conftest test -p policy/aws_rules.rego infrastructure/terraform/
```

### 2. Validate Container Configurations (Docker)
```bash
# For Windows (PowerShell):
conftest test -p policy/docker_rules.rego (Get-ChildItem docker\*\Dockerfile).FullName

# For Linux/Mac (Bash/Zsh):
conftest test -p policy/docker_rules.rego docker/*/Dockerfile
```

### 3. Validate Orchestration Manifests (Kubernetes/Helm)
```bash
helm template sentinel infrastructure/helm/sentinel/ | conftest test -p policy/k8s_rules.rego -
```
