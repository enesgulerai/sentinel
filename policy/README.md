# Enterprise Policy-as-Code (OPA/Conftest)

This directory acts as the central nervous system for our DevSecOps pipeline. We utilize the Open Policy Agent (OPA) and Rego to enforce **Policy-as-Code** across the entire application lifecycle—from how a container is built (Docker), to how it is orchestrated (Kubernetes), to the physical cloud infrastructure it runs on (AWS).

## Why Policy-as-Code?
Manual code reviews are slow and error-prone. By defining our Security, FinOps, and Architectural standards as code, we create an automated "Golden Path." If a developer violates these standards, the CI/CD pipeline immediately catches the flaw and prevents the deployment, ensuring that our production environment remains secure, optimized, and cost-efficient.

---

## 1. Cloud Infrastructure Policies (AWS / Terraform)
Located in `aws_rules.rego`. These policies strictly control our cloud footprint, heavily focusing on the four pillars of modern cloud governance: **FinOps, Network Security, Data Security, and IAM Least Privilege.**

* **FinOps & Governance:** EKS Node Groups are strictly limited to Graviton instances (`t4g.medium`, `t4g.small`) and must use `SPOT` capacity. Legacy `gp2` disks are deprecated in favor of `gp3`.
  * *The "Why":* AWS Graviton provides up to 40% better price-performance. Enforcing SPOT instances and gp3 volumes drastically reduces compute and storage costs.
* **Mandatory Enterprise Tagging:** All critical resources (VPC, EKS Clusters, S3 Buckets) must carry `Environment`, `Owner`, and `Project` tags.
  * *The "Why":* Without strict tagging, granular cloud cost allocation and resource ownership tracking are impossible.
* **Network Security:** Security Groups are prohibited from exposing dangerous ports (e.g., 22, 3306, 5432) to the internet (`0.0.0.0/0`).
  * *The "Why":* Misconfigured Security Groups are the leading cause of cloud breaches. Blocking global access to administrative or database ports prevents brute-force attacks.
* **Data Security:** EBS volumes must be encrypted by default (`encrypted = true`), and S3 buckets can never use a `public-read` ACL.
  * *The "Why":* Ensures data-at-rest is protected against unauthorized physical or logical access, preventing accidental data leaks.
* **IAM Least Privilege:** IAM Policies cannot contain `Action = "*"` or `Resource = "*"`.
  * *The "Why":* Full admin privileges violate the Principle of Least Privilege. If a resource is compromised, restricting IAM scope limits the blast radius.

---

## 2. Containerization Policies (Docker)
Located in `docker_rules.rego`. These policies enforce a zero-exception, enterprise-grade standard for all container images within the project, focusing entirely on supply chain security and size optimization.

* **Strict Multi-Stage Builds:** Single-stage builds are completely forbidden. Every Dockerfile must use at least two `FROM` instructions.
  * *The "Why":* Keeps the final production image incredibly lean by leaving behind build tools, compilers, and temporary downloads (like `curl` or `tar`). This drastically reduces both the image size and the attack surface.
* **Lightweight Base Images Only:** Base images must be a `slim` or `alpine` variant (or `scratch`).
  * *The "Why":* Heavy operating systems contain hundreds of unnecessary packages with potential CVEs (vulnerabilities). Minimal images are significantly more secure, pull faster, and boot faster.
* **No ':latest' Tags:** Pinning explicit version tags is mandatory.
  * *The "Why":* The `:latest` tag is a moving target. Explicit versioning ensures absolute build reproducibility and prevents pipeline breakage when a base image is unexpectedly updated upstream.
* **Enforced Non-Root User:** A `USER` instruction must be present, and the final user cannot be `root`.
  * *The "Why":* Running containers as root is a major security flaw. If a container is compromised, a non-root user prevents the attacker from easily gaining root access to the underlying host or cluster.

---

## 3. Orchestration Policies (Kubernetes)
Located in `k8s_rules.rego`. These rules govern how applications behave once deployed into the EKS cluster, heavily focusing on cluster reliability, security, and FinOps visibility.

* **Resource Management (CFS Protection):** All containers must define resource `requests`. However, setting CPU `limits` is **strictly forbidden**.
  * *The "Why":* Requests are critical for the Kubernetes scheduler to place pods correctly. Intentionally omitting CPU limits prevents CFS (Completely Fair Scheduler) quota throttling, which can artificially degrade application latency even when the underlying node has idle CPU cycles.
* **Pod Security & Isolation:** Containers cannot run with `securityContext.privileged == true`.
  * *The "Why":* Privileged containers bypass namespace isolation. A compromised privileged container can easily escalate privileges to the underlying worker node, putting the entire cluster at risk.
* **Supply Chain & Enterprise FinOps:** Kubernetes deployments cannot use the `:latest` image tag. Additionally, all Pod templates must include mandatory enterprise labels (`environment`, `owner`, `project`).
  * *The "Why":* Banning `:latest` guarantees deployment idempotency and ensures rollbacks are predictable. Enforcing enterprise labels ensures that Kubernetes cost-monitoring tools (like Kubecost) can accurately allocate cluster spending down to the specific microservice and team.

---

## Local Validation (Developer Guide)

You can evaluate your code against these policies locally without waiting for CI/CD feedback. Ensure [Conftest](https://www.conftest.dev/) is installed.

**To test Terraform:**
```bash
conftest test -p policy/aws_rules.rego infrastructure/terraform/
```

**To test Dockerfiles:**
```bash
# For Windows (PowerShell):
conftest test -p policy/docker_rules.rego (Get-ChildItem docker\*\Dockerfile).FullName

# For Linux/Mac (Bash/Zsh):
conftest test -p policy/docker_rules.rego docker/*/Dockerfile

# Alternative for Linux/Mac (If Dockerfiles are nested deeply):
conftest test -p policy/docker_rules.rego $(find docker -name "Dockerfile")
```

**To test K8s Helm Charts:**
```bash
helm template sentinel infrastructure/helm/sentinel/ | conftest test -p policy/k8s_rules.rego -
```
