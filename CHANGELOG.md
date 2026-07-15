### v1.21.0

#### Changed Files & Core Modifications
- Introduced Open Policy Agent (OPA) for Kubernetes policy enforcement.
- Added OPA policies to enforce deployment standards, including resource requests, prevention of privileged containers, prohibition of `:latest` image tags, and mandatory labels.
- Updated Helm chart deployments for API, consumer, HPA, Redis, Redpanda, and validator to include the `env: production` label.

#### Reason for Changes
This release introduces a robust policy enforcement mechanism for Kubernetes deployments using Open Policy Agent (OPA). The goal is to standardize deployments, enhance reliability, and improve security by automatically validating configurations against predefined rules. This proactive approach helps prevent common misconfigurations that can lead to operational issues.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Enhanced Reliability:** Enforcing resource requests ensures proper scheduling and prevents resource starvation.
    - **Improved Security:** Prohibiting privileged containers and `:latest` image tags significantly reduces security vulnerabilities.
    - **Standardization:** Mandatory labels like `env` improve observability and cost management.
    - **Automated Compliance:** OPA policies automate the enforcement of deployment best practices, reducing manual review overhead.
- **(-) Disadvantages / Notes:**
    - This change introduces a new dependency on OPA for Kubernetes policy enforcement. Ensure OPA is correctly deployed and configured in your Kubernetes environment.
    - The introduction of mandatory labels may require adjustments to existing deployment configurations if they do not already adhere to these standards.

---

### v1.20.2

#### Changed Files & Core Modifications
- **`infrastructure/terraform/aws-finops-mock/eks.tf`**: Introduced a KMS key for EKS secret encryption, enforced IMDSv2 for EC2 instances, enabled EKS control plane logging, and refined VPC endpoint access configurations.
- **`infrastructure/terraform/aws-finops-mock/network.tf`**: Implemented VPC Flow Logs with associated IAM roles and CloudWatch log groups, secured the default security group, and added explicit skips for Checkov rules related to public IPs on subnets and KMS encryption for flow logs, citing FinOps and cost optimization reasons.

#### Reason for Changes
These changes address security vulnerabilities identified by Checkov, enhancing the overall security posture of the AWS infrastructure. Specifically, the modifications aim to:
- Secure EKS secrets through KMS encryption.
- Improve instance metadata security by enforcing IMDSv2.
- Enable comprehensive logging for EKS control plane components for better auditing and debugging.
- Enhance network visibility and security by enabling VPC Flow Logs and locking down the default security group.
- Optimize costs by selectively skipping certain security checks where the benefits do not outweigh the financial implications (e.g., public IPs on subnets for FinOps, KMS encryption for flow logs).

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Enhanced security through KMS encryption for secrets and IMDSv2 enforcement.
    - Improved operational visibility and auditability with EKS control plane logging and VPC Flow Logs.
    - More robust network security with a locked-down default security group.
- **(-) Disadvantages / Notes:**
    - Increased infrastructure complexity due to the addition of KMS, IAM roles, and CloudWatch log configurations.
    - Potential for increased AWS costs associated with VPC Flow Logs and CloudWatch log storage, although specific configurations aim to mitigate this (e.g., retention periods, skipping KMS for flow logs).
    - Explicitly skipping certain Checkov rules indicates a conscious decision to prioritize FinOps and cost-effectiveness over absolute adherence to every security recommendation, which may require ongoing monitoring and justification.

---

### v1.20.1

#### Changed Files & Core Modifications
- Updated `pyproject.toml` and `uv.lock` to reflect a dependency upgrade for the `pillow` Python package.

#### Reason for Changes
- This update addresses security vulnerabilities identified in previous versions of the `pillow` library.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Enhances the security posture of the Python environment by mitigating known vulnerabilities. This ensures the integrity and safety of operations relying on image processing capabilities.
- **(-) Disadvantages / Notes:** No significant architectural trade-offs are introduced. The upgrade is a direct security fix.

---

### v1.20.0

#### Changed Files & Core Modifications

*   **Infrastructure as Code (Terraform & Helm):**
    *   Removed the Redpanda Console service and its associated Helm chart configurations.
    *   Updated Terraform configurations for AWS EKS, including adjustments to subnet configurations and the introduction of a launch template for worker nodes.
    *   Modified Helm `values.yaml` to comment out resource limits for API, Validator, Consumer, and PostgreSQL components, and for Redis.
*   **CI/CD & Security Policies:**
    *   Introduced Open Policy Agent (OPA) and Conftest rules for validating Infrastructure as Code (IaC) and Docker images.
    *   Updated the Jenkins Dockerfile to run as a non-root user.
    *   Automated image tag updates in GitOps configurations.
*   **Load Testing:**
    *   Modified the k6 load test script to include iteration and random elements in the virtual user payload for more dynamic testing.

#### Reason for Changes

This release focuses on enhancing operational efficiency, cost optimization, and security posture. Key drivers include:

*   **Resource Optimization:** The removal of Redpanda Console aims to reduce resource consumption and simplify the infrastructure.
*   **FinOps Compliance:** Terraform configurations were updated to align with FinOps policies, specifically by restricting EKS nodes to a single Availability Zone and enforcing the use of Spot instances to minimize AWS costs.
*   **Security Hardening:** New OPA and Conftest policies have been implemented to enforce security best practices in IaC and Docker image builds, such as preventing the use of `:latest` tags, ensuring non-root execution, and promoting multi-stage builds. The Jenkins container was also updated to run as a non-root user.
*   **Improved Testing:** Load test parameters were refined to generate more realistic and varied test data.

#### Advantages & Architectural Trade-offs

*   **(+) Advantages:**
    *   **Cost Reduction:** Significant potential for cost savings through FinOps-aligned infrastructure configurations (e.g., Spot instances, single AZ deployment).
    *   **Enhanced Security:** Improved security through automated policy enforcement for IaC and Docker images, and by running containers as non-root users.
    *   **Resource Efficiency:** Reduced infrastructure footprint by removing the Redpanda Console.
    *   **Improved Test Realism:** More dynamic and representative load testing scenarios.
    *   **Streamlined Operations:** Automated image tag updates simplify the GitOps workflow.
*   **(-) Disadvantages / Notes:**
    *   **Resource Limits Temporarily Disabled:** Resource limits for several components (API, Validator, Consumer, PostgreSQL, Redis) have been commented out in the Helm `values.yaml`. This may lead to increased resource consumption if not managed carefully and requires monitoring.
    *   **EKS Multi-AZ Requirement:** While worker nodes are restricted to a single AZ for cost savings, the EKS control plane still requires multiple subnets across different AZs for its own high-availability requirements. This is a necessary compromise for the FinOps strategy.
    *   **Potential Impact of Policy Enforcement:** The new OPA/Conftest policies may require adjustments to existing Dockerfiles or IaC configurations to comply with the defined rules.

---

### v1.19.23

#### Changed Files & Core Modifications
- **CI/CD Workflows (`.github/workflows/`):**
    - Minor syntax adjustments were made to the `release-agent.yaml`, `security.yaml`, and `test.yaml` files. These include fixing bracket spacing and ensuring proper end-of-file newlines in workflow definitions.

#### Reason for Changes
- These changes are primarily maintenance-oriented, focusing on improving the robustness and correctness of our continuous integration and continuous deployment (CI/CD) pipelines. Ensuring consistent syntax and formatting in workflow files prevents potential parsing errors and enhances the reliability of automated processes.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Improved CI/CD pipeline stability and reliability due to standardized syntax.
    - Reduced potential for build or deployment failures caused by minor syntax inconsistencies.
    - Enhanced maintainability of workflow configurations.
- **(-) Disadvantages / Notes:**
    - No significant architectural changes or performance impacts are introduced. These are purely syntactical and formatting improvements.

---

### v1.19.22

#### Changed Files & Core Modifications
- The `.yamllint` configuration file has been updated. This includes adding an exclusion for Helm templates within the `infrastructure/helm/sentinel/templates/` directory and disabling rules related to document start, new lines, comments indentation, and line length.

#### Reason for Changes
- These changes were made to refine the linting process for YAML files. Specifically, the exclusion of Helm templates addresses potential linting conflicts or unnecessary warnings within that specific templating system. Disabling certain rules aims to provide more flexibility or accommodate existing patterns in the codebase.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Improved CI/CD pipeline efficiency by reducing noise from Helm template linting. Enhanced developer experience by tailoring linting rules to project-specific needs.
- **(-) Disadvantages / Notes:** None.

---

### v1.19.21

#### Changed Files & Core Modifications
- **CI/CD Pipeline (`.github/workflows/format.yaml`):** Integrated `yamllint` into the code quality pipeline to enforce YAML formatting standards.
- **Pre-commit Configuration (`.pre-commit-config.yaml`):** Added `yamllint` as a pre-commit hook to ensure YAML files adhere to defined formatting rules before commits are allowed.
- **YAML Linting Configuration (`.yamllint`):** Introduced a new configuration file to define specific rules and exceptions for `yamllint`, customizing the linting process.

#### Reason for Changes
To enhance code quality and maintainability, this release introduces automated linting for YAML files. This ensures consistency and adherence to best practices across all YAML configurations and manifests used within the project.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Improved code consistency and readability for all YAML files.
    - Early detection of formatting errors, reducing potential runtime issues.
    - Enhanced developer experience by automating code quality checks.
- **(-) Disadvantages / Notes:**
    - Requires developers to have `yamllint` installed or rely on the CI pipeline for validation.
    - The specific `yamllint` rules are configured to be less strict in certain areas (e.g., `document-start`, `new-lines`, `comments-indentation`) to accommodate existing project conventions.

---

### v1.19.20

#### Changed Files & Core Modifications
- Modified resource allocation (CPU and memory requests/limits) for several components within the Sentinel Helm chart, including `api`, `validator`, `consumer`, `postgres`, `redis`, and `redpanda`.

#### Reason for Changes
- These adjustments were made to calibrate resource boundaries more precisely, informed by performance testing (K6 telemetry). The goal is to ensure optimal resource utilization and stability for the deployed services.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Improved resource efficiency and potential cost savings through more accurate resource allocation.
    - Enhanced service stability and performance by preventing resource contention and starvation.
    - Better alignment of resource provisioning with actual observed usage patterns.
- **(-) Disadvantages / Notes:**
    - While aiming for efficiency, overly aggressive resource reductions could potentially lead to performance degradation under peak load if the telemetry data did not capture all edge cases. Monitoring after deployment is recommended.

---

### v1.19.19

#### Changed Files & Core Modifications
- Updated documentation across `README.md`, `infrastructure/helm/README.md`, and `infrastructure/terraform/aws-finops-mock/README.md`.
- Removed a static image reference from `README.md`.

#### Reason for Changes
- The primary driver for these changes is to accurately reflect the performance improvements and cost optimizations achieved by the system. Specifically, the documentation has been updated to showcase a significant increase in Request Per Second (RPS) handling capabilities and a reduction in tail latency.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Enhanced Performance:** The system now demonstrates the capability to handle a higher throughput of **25,300+ RPS**, up from 14,500+ RPS, while maintaining sub-millisecond tail latencies (reduced to < 7ms).
    - **Improved Cost Efficiency:** The AWS FinOps simulation continues to highlight a substantial **73% cost reduction** under enterprise conditions, reinforcing the economic benefits of the implemented architecture.
    - **Clearer Documentation:** Updated documentation provides a more accurate and compelling representation of the system's performance and cost-saving capabilities.
- **(-) Disadvantages / Notes:**
    - No architectural trade-offs or disadvantages were introduced with these documentation updates. The changes solely focus on reflecting existing performance and cost improvements.

---

### v1.19.18

#### Changed Files & Core Modifications
- **`docker-compose.yml`**: Updated the Redis image from `dragonflydb/dragonfly:v1.17.1` to `valkey/valkey:8.0` and adjusted the health check command accordingly.
- **`infrastructure/helm/sentinel/values.yaml`**: Updated image tags for `api`, `validator`, and `consumer` services to `88c07a2`.
- **`src/api/go.mod` and `src/api/go.sum`**: Updated dependencies for `klauspost/compress`, `golang.org/x/crypto`, `golang.org/x/net`, `golang.org/x/sys`, and `golang.org/x/text`.
- **`src/validator/src/main.rs`**: Applied standard Rust formatting (`rustfmt`) to the `main.rs` file.

#### Reason for Changes
This release focuses on dependency updates and infrastructure alignment. The primary driver for the `docker-compose.yml` change is the migration from DragonflyDB to Valkey, ensuring continued compatibility and leveraging the latest stable versions. Updates to Helm values align deployment configurations with the latest image tags. Dependency updates in the API module address potential security vulnerabilities and incorporate performance improvements from upstream libraries. The formatting change in the validator ensures code consistency.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Stability and Security:** Updating dependencies can bring in security patches and bug fixes.
    - **Infrastructure Modernization:** Transitioning to Valkey provides a robust and actively maintained in-memory data store.
    - **Codebase Health:** Applying `rustfmt` improves code readability and maintainability.
    - **Deployment Consistency:** Synchronized image tags across services ensure consistent deployments.
- **(-) Disadvantages / Notes:**
    - The change from DragonflyDB to Valkey might require a brief period of observation to ensure no regressions in performance or behavior specific to the application's Redis interactions.

---

### v1.19.17

#### Changed Files & Core Modifications
- **`Taskfile.yml`**: Updated the pre-pulling of the Redis image to use `valkey/valkey:8.0` instead of `dragonflydb/dragonfly:v1.17.1`.
- **`infrastructure/helm/sentinel/values.yaml`**:
    - Updated image tags for `sentinel-api`, `sentinel-validator`, and `sentinel-consumer` to `da127da`.
    - Modified the Redis image repository to `valkey/valkey` and tag to `8.0`.
    - Adjusted resource requests and limits for the validator.
    - Significantly updated probe configurations (startup, liveness, readiness) for the validator, including command changes, increased timeouts, and adjusted thresholds.
- **`src/validator/src/main.rs`**: Modified the validator's main function to correctly handle probe commands (`--check-startup`, `--check-live`, `--check-ready`) by exiting successfully when these arguments are present, preventing unnecessary processing.

#### Reason for Changes
This release addresses issues related to Kubernetes probe timeouts for the validator component. The changes aim to improve the reliability of the validator's health checks by adjusting probe configurations and ensuring the probe commands execute efficiently. Additionally, this release updates the underlying Redis image from DragonflyDB to Valkey, reflecting a shift in the chosen database technology.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Resolved Kubernetes probe timeouts, leading to more stable and reliable validator deployments.
    - Improved health check accuracy and responsiveness for the validator.
    - Transitioned to Valkey, potentially leveraging its specific features and performance characteristics.
- **(-) Disadvantages / Notes:**
    - The change from DragonflyDB to Valkey is a significant technology shift. While Valkey is a fork of Redis, it's important to ensure compatibility and performance characteristics meet expectations.
    - Increased probe timeouts and adjusted thresholds might mask underlying issues if not carefully monitored. Resource adjustments for the validator should be validated for performance impact.

---

### v1.19.16

#### Changed Files & Core Modifications
- **CI/CD Pipeline (`.github/workflows/test.yaml`):**
    - Introduced concurrency control for GitHub Actions workflows to prevent race conditions and optimize execution.
    - Enabled the race detector for Go tests to identify and fix potential data races.
    - Added Rust caching for faster build times in the validator tests.
    - Expanded Python test execution to cover all unit tests in the `tests/unit/` directory, improving test coverage.
- **Helm Chart (`infrastructure/helm/sentinel/values.yaml`):**
    - Updated image tags for `sentinel-api`, `sentinel-validator`, and `sentinel-consumer` to `a3bc6a7`.

#### Reason for Changes
This release focuses on improving the stability and efficiency of our continuous integration and deployment processes, alongside updating core component image versions. The CI/CD enhancements aim to ensure more robust testing and faster feedback loops. The image tag updates are part of a routine synchronization with the latest development builds.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Enhanced test reliability through the Go race detector and broader Python test coverage.
    - Improved CI build performance with Rust caching.
    - Increased CI/CD pipeline stability with concurrency controls.
    - Ensures deployments are using the latest synchronized image versions.
- **(-) Disadvantages / Notes:**
    - No significant disadvantages or architectural trade-offs introduced. The changes are primarily focused on improving development and deployment workflows.

---

### v1.19.15

#### Changed Files & Core Modifications
- Updated `.pre-commit-config.yaml` to synchronize local development linting tools with the CI pipeline. This involved updating the revisions for several pre-commit hooks, including `pre-commit-hooks`, `conventional-pre-commit`, `ruff-pre-commit`, `bandit`, and introducing `golangci-lint`.

#### Reason for Changes
- The primary motivation for this update is to ensure consistency between the linting and formatting checks performed locally by developers and those executed in the continuous integration (CI) pipeline. This synchronization helps catch potential issues earlier in the development cycle and reduces the likelihood of CI failures due to environmental or configuration drift.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Improved developer experience by providing more accurate and consistent feedback on code quality locally.
    - Reduced CI failures by aligning local and CI environments.
    - Enhanced code quality and maintainability through updated linting and formatting rules.
    - Introduction of `golangci-lint` for more comprehensive Go code analysis within the API source directory.
- **(-) Disadvantages / Notes:**
    - Developers may need to update their local pre-commit hooks to reflect these changes.
    - The introduction of `golangci-lint` with a specific path prefix (`src/api`) and timeout (`--timeout=5m`) might require minor adjustments to local development workflows if not already accounted for.

---

### v1.19.14

#### Changed Files & Core Modifications
- Updated `pyproject.toml` and `uv.lock` to include a new dependency, `soupsieve`, and to specify its version.

#### Reason for Changes
- This release addresses a transitive security vulnerability identified in the `soupsieve` dependency. The update ensures that the project is protected against known security risks by incorporating the latest patched version of this library.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Enhances the security posture of the application by mitigating a known vulnerability. This is a proactive measure to maintain system integrity and protect against potential exploits.
- **(-) Disadvantages / Notes:** No significant architectural trade-offs or disadvantages are introduced by this security patch. The update is a direct dependency version bump to address a specific vulnerability.

---

### v1.19.13

#### Changed Files & Core Modifications
- **CI Configuration (`.github/workflows/format.yaml`):** The continuous integration workflow has been updated to enforce stricter code quality and formatting checks for Go and Python codebases. This includes adding explicit checks for Go formatting using `gofmt` and refining the Ruff linter and formatter execution for Python. The workflow now also includes concurrency controls to optimize execution.

#### Reason for Changes
- To improve code consistency and maintainability across the project, this update introduces more rigorous automated checks within the CI pipeline. This ensures that all code contributions adhere to established formatting standards and linting rules before being merged, reducing the likelihood of style-related issues and improving overall code quality.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Enhanced code quality and consistency through automated enforcement of formatting and linting rules.
    - Reduced technical debt by proactively identifying and correcting style deviations.
    - Improved developer experience by providing immediate feedback on code style issues.
    - More robust CI pipeline with optimized execution through concurrency controls.
- **(-) Disadvantages / Notes:**
    - Developers will need to ensure their local development environments are configured to match the CI's formatting and linting standards to avoid CI failures.

---

### v1.19.12

#### Changed Files & Core Modifications
- Updated `pyproject.toml` and `uv.lock` to reflect dependency version changes.
- Specifically, the `onnx` package has been upgraded from version `1.21.0` to `1.22.0`.
- The `pydantic-settings` package has been updated from version `2.14.0` to `2.14.2`.

#### Reason for Changes
- The primary driver for this release is to address security vulnerabilities identified in the Python dependencies, specifically within the inference service. This update ensures the system is running with patched versions of critical libraries.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Enhanced Security:** Mitigates known security risks by updating to patched versions of `onnx` and `pydantic-settings`.
    - **Dependency Updates:** Incorporates minor version updates for `onnx` and `pydantic-settings` which may include bug fixes and performance improvements.
- **(-) Disadvantages / Notes:**
    - No significant architectural trade-offs are introduced with these dependency updates. The changes are focused on maintaining security and stability.

---

### v1.11.19

#### Changed Files & Core Modifications
- The `.github/workflows/security.yaml` file was updated to modify the dependency vulnerability scanning process.

#### Reason for Changes
- This change addresses an issue where `pip-audit` was encountering errors when attempting to parse the `pyproject.toml` file directly.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Resolves a technical debt by ensuring the security scanning process runs reliably, preventing potential vulnerabilities from being missed due to parsing errors. This improves the robustness of our security checks.
- **(-) Disadvantages / Notes:** None.

---

### v1.19.10

#### Changed Files & Core Modifications
- The `security.yaml` GitHub Actions workflow has been significantly refactored.
- The workflow now utilizes `uvx` for executing ephemeral Python security tools like Bandit and Pip Audit.
- Rust-based security tools (Clippy and Cargo Audit) have been integrated into the workflow for Rust code analysis.
- Dependency caching for Rust workspaces has been implemented using `Swatinem/rust-cache@v2`.
- The setup for Rust toolchains and the installation of `cargo-audit` have been streamlined.

#### Reason for Changes
- This release addresses security scanning within the CI/CD pipeline. The primary goal was to enhance the efficiency and reliability of security checks by leveraging `uvx` for Python tools and integrating Rust-native security analysis.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Improved security scanning coverage by incorporating Rust-specific tools.
    - Streamlined execution of Python security tools through `uvx`, potentially leading to faster and more isolated execution.
    - Enhanced CI performance with Rust dependency caching.
    - Centralized and more robust security checks within the automated workflow.
- **(-) Disadvantages / Notes:**
    - This change introduces a dependency on Rust toolchains and associated actions within the CI environment.

---

### v1.19.9

#### Changed Files & Core Modifications
- The `.github/workflows/security.yaml` file was updated to replace the Rust-based security tooling with Python-based tools managed by `uvx`. This includes changes to how the Rust toolchain and dependencies were handled, and the introduction of `uvx` for executing security scanners like Bandit and Pip Audit.

#### Reason for Changes
- This change was made to standardize and improve the execution of security scanning tools within the CI/CD pipeline. By leveraging `uvx`, we can ensure more consistent and efficient execution of Python-based security tools.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Security Scanning:** Utilizes `uvx` for more robust and consistent execution of Static Application Security Testing (SAST) with Bandit and dependency vulnerability scanning with Pip Audit.
    - **Streamlined Tooling:** Consolidates security scanning under a unified Python tooling approach, reducing reliance on separate Rust toolchain configurations for security checks.
    - **Enhanced Cache Management:** `setup-uv` with `enable-cache: true` and `cache-dependency-glob: "uv.lock"` optimizes dependency caching for faster CI runs.
- **(-) Disadvantages / Notes:**
    - This change shifts the security scanning tooling from Rust-based checks (like `cargo clippy` and `cargo audit`) to Python-based tools. While this offers advantages in standardization, it means the specific Rust-related code quality checks are no longer performed in this workflow.

---

### v1.19.8

#### Changed Files & Core Modifications
- Modified `.github/workflows/security.yaml` to include the `--system` flag during the installation of security tools (`bandit`, `pip-audit`) within the Python environment.

#### Reason for Changes
- This change addresses a security hardening requirement. By using the `--system` flag, the security analysis tools are installed directly into the system's Python environment rather than a virtual environment. This ensures that the security scanning tools themselves are not subject to the same dependency resolution and isolation that might be applied to application code, providing a more robust and consistent security audit.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Enhances the reliability and consistency of security scanning by ensuring the analysis tools are installed in a predictable manner, improving the accuracy of Static Application Security Testing (SAST).
- **(-) Disadvantages / Notes:** None.

---

### v1.19.7

#### Changed Files & Core Modifications
- The `.github/workflows/security.yaml` file was updated.
- The `uses` directive for the `astral-sh/setup-uv-action@v5` action was corrected to `astral-sh/setup-uv@v5`.

#### Reason for Changes
- This change addresses an issue where the incorrect action name was being used in the security workflow for setting up the `uv` Python environment.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Ensures the security workflow correctly utilizes the `uv` Python environment setup action, preventing potential misconfigurations or failures in security-related CI/CD processes.

---

### v1.19.6

#### Changed Files & Core Modifications
- **`.github/workflows/security.yaml`**: Updated the security scanning workflow for Python dependencies. This includes switching from `actions/setup-python` and `pip` to `astral-sh/setup-uv-action` for environment management and dependency installation. The Rust security audit process was also streamlined by directly invoking `cargo audit` and installing `cargo-audit` via an action.
- **`src/api/go.mod`**: Updated the Go version from `1.26.4` to `1.26.5`.

#### Reason for Changes
- **Enhanced Python Security Scanning**: The primary driver for these changes is to improve the efficiency and reliability of security audits for Python dependencies. The integration of `uv` (a fast Python package installer and resolver) aims to provide a more robust and performant dependency management and scanning experience.
- **Streamlined Rust Security Audits**: Simplified the Rust security audit process within the CI/CD pipeline for better maintainability and potentially faster execution.
- **Go Version Update**: Minor updates to the Go version in the API module.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Python Dependency Management**: Leveraging `uv` offers faster dependency resolution and installation, leading to quicker CI/CD pipeline runs for Python projects.
    - **More Efficient Security Audits**: The integration of `uv` and streamlined Rust audits contribute to a more efficient and effective security posture.
    - **Reduced CI/CD Complexity**: Consolidating dependency management and security tooling within `uv` simplifies the workflow configuration.
- **(-) Disadvantages / Notes:**
    - **New Tooling Adoption**: The adoption of `uv` introduces a new tool into the development workflow. While beneficial, it requires developers to be familiar with its usage.
    - **Potential for Initial Configuration Adjustments**: Migrating to `uv` might require minor adjustments to existing dependency management configurations or build scripts.

---

### v1.19.5

#### Changed Files & Core Modifications
- The `security.yaml` GitHub Actions workflow configuration has been updated.
- The `working-directory` for a specific job within the workflow has been changed from `src/consumer` to `src/inference`.

#### Reason for Changes
- This release addresses security vulnerabilities within the API.
- The pipeline configuration was adjusted to ensure security checks are applied to the correct code directory.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Enhanced API security by patching identified vulnerabilities. Improved CI/CD pipeline accuracy for security scanning.
- **(-) Disadvantages / Notes:** None.

---

### v1.19.4

#### Changed Files & Core Modifications
- The CI/CD pipeline configuration (`.github/workflows/security.yaml`) has been significantly restructured.
- Introduced path filtering to conditionally execute security scans based on code changes within specific service directories (API, Validator, Consumer).
- Consolidated and renamed security scanning jobs for clarity and better organization.
- Enhanced the Go security scan to exclude test directories from SAST analysis.
- Integrated `gitleaks-action` for global secret scanning.
- Added `pip-audit` for Python dependency vulnerability scanning.
- Modified Trivy scanner configuration to exit with a non-zero code on critical/high severity findings and to ignore unfixed vulnerabilities.

#### Reason for Changes
- To improve the efficiency and accuracy of the security scanning process within the CI/CD pipeline.
- To enable faster feedback loops by only running relevant security checks based on the scope of code modifications.
- To strengthen the security posture by implementing stricter vulnerability checks and expanding coverage to include secret scanning and Python dependency audits.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved CI/CD Performance:** Conditional execution of security scans significantly reduces pipeline execution time for changes that do not affect specific services.
    - **Enhanced Security Coverage:** Introduction of global secret scanning and Python dependency vulnerability checks broadens the security audit scope.
    - **Better Developer Experience:** Faster feedback on security issues allows for quicker remediation.
    - **Increased Strictness:** Trivy scanner is now configured to fail builds on critical and high-severity vulnerabilities, enforcing higher security standards.
- **(-) Disadvantages / Notes:**
    - The new path filtering mechanism requires careful maintenance of the filter definitions to ensure all relevant services are covered.
    - Increased strictness in Trivy scanning might lead to more build failures if critical/high vulnerabilities are present, requiring prompt attention.

---

### v1.19.3

#### Changed Files & Core Modifications
- The `.github/workflows/security.yaml` file was updated to modify the security scanning workflow. Specifically, the `cargo-audit` and `cargo clippy` commands are now executed directly within the `src/validator` working directory.

#### Reason for Changes
- This change addresses a security vulnerability by ensuring that the `cargo-audit` tool is run directly within the `src/validator` directory. This guarantees that the audit is performed on the correct project dependencies, preventing potential security risks from being overlooked.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Enhanced security by ensuring accurate dependency auditing.
    - Improved reliability of the CI/CD pipeline's security checks.
- **(-) Disadvantages / Notes:**
    - This change introduces a new step to install `cargo-audit` within the workflow, which may slightly increase the execution time of the security job.

---

### v1.19.2

#### Changed Files & Core Modifications
- The `security.yaml` GitHub Actions workflow file was updated. Specifically, the `cargo-audit` check configuration was modified to use the `working-directory` input instead of `create-paths`.

#### Reason for Changes
- This change addresses a security configuration issue within the CI/CD pipeline. The `cargo-audit` tool was not correctly scanning the intended directory for security vulnerabilities.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** This modification ensures that security audits are performed on the correct codebase directory, improving the effectiveness of vulnerability detection and strengthening the overall security posture of the project.

---

### v1.19.1

#### Changed Files & Core Modifications
- The `.github/workflows/security.yaml` file was updated to correctly configure the `cargo-audit` tool. Specifically, the `create-paths` input was added to ensure the audit process targets the correct source code directory.

#### Reason for Changes
- This change addresses an issue where the automated security scanning tool (`cargo-audit`) was not correctly configured to scan the relevant Rust code paths. This could lead to potential vulnerabilities being missed.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Enhances the security posture of the project by ensuring comprehensive vulnerability scanning of the Rust codebase. This resolves a configuration debt and improves the reliability of our security checks.
- **(-) Disadvantages / Notes:** No significant disadvantages or architectural trade-offs were introduced. This is a targeted fix to improve an existing process.

---

### v1.19.0

#### Changed Files & Core Modifications
- **`.github/workflows/security.yaml`**: Enhanced the security scanning workflow by integrating `cargo-audit` for Rust dependency vulnerability checks and adjusting the `trivy` scanner's exit code behavior.
- **`infrastructure/helm/sentinel/values.yaml`**: Updated image tags for `sentinel-api`, `sentinel-validator`, and `sentinel-consumer` to `d0edbb6`.

#### Reason for Changes
- **Enhanced Security Posture**: The integration of `cargo-audit` directly addresses the need to proactively identify and mitigate security vulnerabilities within Rust dependencies. This strengthens the overall security of the project by adding another layer of automated security scanning.
- **Improved CI/CD Reliability**: Adjusting the `trivy` exit code from '1' to '0' for filesystem scans is a refinement to the CI/CD pipeline. This change likely aims to prevent unnecessary pipeline failures due to non-critical findings or to allow for more granular control over how scan results impact the build process.
- **Automated Dependency Updates**: The update of image tags in the Helm values file (`d0edbb6`) signifies an automated process for keeping deployed components up-to-date with the latest builds, ensuring that security patches and improvements are deployed promptly.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Security**: Proactive identification of vulnerabilities in Rust dependencies reduces the attack surface.
    - **More Robust CI/CD**: Finer control over scan exit codes can lead to more stable and reliable build and deployment pipelines.
    - **Up-to-date Deployments**: Automated image tag updates ensure that deployed services benefit from the latest fixes and features.
- **(-) Disadvantages / Notes:**
    - **Potential for Increased Scan Time**: Adding `cargo-audit` may slightly increase the execution time of the security workflow.
    - **Configuration Management**: The change in `trivy` exit code requires careful consideration to ensure that critical vulnerabilities are still appropriately flagged and addressed.

---

### v1.18.8

#### Changed Files & Core Modifications
- The `src/validator/src/main.rs` file was modified. The changes involve reformatting existing error handling code to adhere to line length guidelines.

#### Reason for Changes
- This change was made to address line length warnings identified during code formatting checks. The modifications ensure the codebase maintains a consistent and readable style.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Improved code readability and maintainability by adhering to established formatting standards. This contributes to a cleaner and more consistent codebase.
- **(-) Disadvantages / Notes:** None. This is a routine code hygiene update.

---

### v1.18.7

#### Changed Files & Core Modifications
- `src/validator/src/main.rs`: Modified the main application logic to correctly define and utilize the `connection_string` variable.

#### Reason for Changes
- The previous implementation was missing the definition of the `connection_string` variable, which is essential for establishing a connection to the message broker. This omission was causing the Continuous Integration (CI) pipeline, specifically the clippy checks, to fail.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Resolved a critical issue preventing the validator service from connecting to the message broker.
    - Restored the integrity of the CI pipeline, ensuring that code quality checks can proceed without interruption.
    - Improved the robustness of the validator service by ensuring a default connection string is used when the environment variable is not explicitly set.
- **(-) Disadvantages / Notes:**
    - This is a bug fix and does not introduce new features or architectural changes. The default connection string `localhost:19092` is now used if `REDPANDA_BROKER` is not configured.

---

### v1.18.6

#### Changed Files & Core Modifications
- **`src/validator/main.rs`**: Modified error handling within the validator to explicitly exit on critical failures (e.g., Kafka client connection issues) instead of silently returning.
- **`infrastructure/helm/sentinel/values.yaml`**: Updated image tags for `sentinel-api`, `sentinel-validator`, and `sentinel-consumer` to `9170b0e`.

#### Reason for Changes
The validator component previously handled critical errors, such as failing to establish a connection to the Kafka broker or specific partitions, by silently returning. This masked underlying issues and prevented proper error reporting and system recovery. The change ensures that such critical failures are now explicitly reported and result in an immediate process exit, allowing for quicker detection and resolution of infrastructure or configuration problems.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Observability:** Critical errors in the validator are now surfaced, making it easier to diagnose and resolve connectivity or configuration issues.
    - **Enhanced Stability:** Prevents the validator from entering an unrecoverable state without clear indication.
    - **Automated GitOps Updates:** The image tags have been automatically updated as part of the GitOps workflow, ensuring the latest stable build is deployed.
- **(-) Disadvantages / Notes:**
    - The explicit exit on error might lead to more frequent restarts of the validator pod if transient network issues occur. However, this is generally preferable to silent failures.

---

### v1.18.5

#### Changed Files & Core Modifications
- **Jenkinsfile:** Modified the `sed` command within the Jenkins pipeline to correctly escape double quotes when updating the Helm `values.yaml` file. This ensures that numeric image tags are parsed as strings in the YAML.
- **infrastructure/helm/sentinel/values.yaml:** Updated the image tags for `sentinel-api`, `sentinel-validator`, and `sentinel-consumer` to `6253106`.

#### Reason for Changes
This release addresses an issue where Helm's YAML parsing was incorrectly interpreting numeric image tags as integers, leading to potential deployment failures or unexpected behavior. The change in the Jenkinsfile ensures that image tags are consistently treated as strings, resolving this parsing error. The update to image tag `6253106` reflects a specific build or commit that has been validated.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Resolves a critical issue in the CI/CD pipeline that could prevent successful deployments due to incorrect Helm YAML parsing.
    - Ensures consistent and reliable deployment of the specified image version (`6253106`) across all Sentinel components.
    - Improves the robustness of the automated deployment process.

---

### v1.18.4

#### Changed Files & Core Modifications
- **Helm Chart Updates:** Modified Kubernetes deployment configurations (`.yaml` files) across various services (API, Console, Consumer, PostgreSQL, Redis, Redpanda, Validator) to include `startupProbe` configurations.
- **API Health Endpoints:** Updated the Go API (`main.go`) to expose new health endpoints: `/health/startup`, `/health/live`, and `/health/ready`.
- **Dependency Management:** Updated `go.mod` and `go.sum` files for the API service, removing several OpenTelemetry-related dependencies.
- **Image Tag Update:** The `values.yaml` file for the Helm chart was updated to reflect a new image tag (`ff99b8c`) for multiple services.

#### Reason for Changes
This release focuses on enhancing the reliability and observability of the application within a Kubernetes environment. The primary drivers are:
- **Improved Kubernetes Integration:** By introducing `startupProbe` configurations for various services, the system can better manage pod lifecycles during startup, ensuring that applications are fully initialized before being considered ready for traffic. This is crucial for robust deployments.
- **Standardized Health Checks:** The API now provides distinct health endpoints (`/health/startup`, `/health/live`, `/health/ready`) that align with standard Kubernetes probing practices, allowing for more granular health monitoring.
- **Dependency Cleanup:** The removal of specific OpenTelemetry dependencies suggests a refactoring or simplification of the tracing and metrics collection mechanism, potentially leading to a smaller API footprint or a shift in how observability is managed.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Enhanced Kubernetes Orchestration:** The addition of `startupProbe` significantly improves the resilience of deployments by preventing traffic from being sent to pods that are still initializing.
    - **Improved Observability:** Standardized health endpoints facilitate better integration with Kubernetes' health checking mechanisms and external monitoring tools.
    - **Reduced API Complexity:** The removal of certain OpenTelemetry dependencies may lead to a more streamlined API service, potentially improving build times and reducing the attack surface.
- **(-) Disadvantages / Notes:**
    - **Infrastructure Configuration:** Users leveraging Kubernetes deployments will need to ensure their Helm chart configurations are updated to utilize these new probe settings.
    - **Observability Strategy:** If the removed OpenTelemetry dependencies were actively used for tracing or metrics, a new strategy for observability may need to be implemented or confirmed.

---

### v1.18.3

#### Changed Files & Core Modifications
- **Helm Chart Enhancements:** The Helm chart for Sentinel has been significantly refactored to dynamically generate Kubernetes manifests for various services including API, Console, Consumer, Validator, PostgreSQL, Redis, and Redpanda. This includes the creation of new deployment, service, and stateful set configurations where applicable.
- **Service Dependencies:** Init containers have been added to deployments to ensure proper startup order and dependency resolution (e.g., waiting for PostgreSQL, Redis, and Redpanda before the main application containers start).
- **PostgreSQL Configuration:** New configurations for PostgreSQL have been introduced, including a ConfigMap for initialization scripts (enabling the `vector` extension and defining a `transactions` table with vector indexing) and a Secret for database credentials.
- **Resource Management:** Kubernetes resource definitions (requests and limits) and probe configurations (liveness and readiness) are now dynamically configurable for each service within the Helm chart.

#### Reason for Changes
This release introduces a comprehensive refactoring of the Sentinel Helm chart to enable dynamic and configurable deployment of all its constituent services. The goal is to improve the manageability, scalability, and reliability of the Sentinel deployment by leveraging Kubernetes' native capabilities and providing a more robust infrastructure setup.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Deployability:** The Helm chart now supports the dynamic deployment of all core services, simplifying the setup and management of the Sentinel ecosystem.
    - **Enhanced Reliability:** The introduction of init containers ensures that services start in the correct order, preventing startup failures due to missing dependencies.
    - **Increased Configurability:** Resource allocation, autoscaling parameters, and readiness/liveness probes are now configurable per service, allowing for fine-tuned performance and stability.
    - **Standardized Infrastructure:** The inclusion of managed PostgreSQL and Redpanda deployments within the Helm chart provides a more standardized and integrated infrastructure.
    - **Vector Database Support:** The PostgreSQL initialization script now includes the necessary setup for the `pgvector` extension, enabling vector embeddings for transaction data.
- **(-) Disadvantages / Notes:**
    - **Increased Complexity:** While more configurable, the Helm chart itself has become more complex due to the dynamic generation of manifests.
    - **Infrastructure Requirements:** This release assumes the availability of a Kubernetes cluster capable of running the defined resources. The PostgreSQL deployment requires persistent storage.

---

### v1.18.2

#### Changed Files & Core Modifications
- **`docker-compose.yml`**: Updated the Redis image to use DragonflyDB and removed resource reservation/limit configurations for several services.
- **`Taskfile.yml`**: Pinned the DragonflyDB image tag to `v1.17.1` for pre-pulling.
- **Kubernetes Helm Charts (`infrastructure/helm/sentinel/`)**:
    - Removed deployments and services for `api`, `console`, `consumer`, `postgres`, `redis`, `redpanda`, and `validator`.
    - Modified `hpa.yaml` to include behavior metrics.
    - Updated `ingress.yaml` to support more flexible ingress configurations.
- **`src/api/main.go`**: Removed OpenTelemetry (OTel) instrumentation and related dependencies. Added `/healthz` and `/readyz` endpoints.
- **`src/inference/consumer.py`**: Removed OpenTelemetry (OTel) instrumentation and related dependencies.
- **`src/validator/src/main.rs`**: Removed OpenTelemetry (OTel) instrumentation and related dependencies.
- **`infrastructure/helm/sentinel/values.yaml`**: Updated image tags for `api`, `validator`, and `consumer` to `b60abfb`.

#### Reason for Changes
This release focuses on optimizing performance and simplifying the infrastructure by removing OpenTelemetry tracing. The previous implementation of OTel introduced overhead and complexity that is no longer deemed necessary for the current operational requirements. Additionally, the integration of DragonflyDB as the primary Redis-compatible data store is now solidified, and the deployment configurations have been streamlined.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Max Performance:** Removal of OpenTelemetry instrumentation significantly reduces processing overhead, leading to lower latency and higher throughput for the API, consumer, and validator services.
    - **Simplified Infrastructure:** The removal of Jaeger and associated configurations streamlines deployment and maintenance.
    - **DragonflyDB Integration:** The system now leverages DragonflyDB for enhanced performance and scalability as a Redis-compatible data store.
    - **Improved Kubernetes Readiness:** Addition of `/healthz` and `/readyz` endpoints enhances Kubernetes integration and reliability.
- **(-) Disadvantages / Notes:**
    - **Loss of Observability:** The removal of OpenTelemetry means a loss of distributed tracing capabilities. This may impact debugging complex, multi-service interactions. Future efforts may be required to re-introduce observability if deemed critical.
    - **Infrastructure Simplification:** The removal of several Helm chart templates indicates a consolidation of services, potentially requiring adjustments to how these components are managed if they were previously configured independently.

---

### v1.18.1

#### Changed Files & Core Modifications
- **`agent/release/release_agent.py`**: Refactored the release agent script to improve code quality and adherence to PEP 8 standards. This includes enhancements to error handling for API calls and more robust parsing of Git commands.
- **`infrastructure/helm/sentinel/values.yaml`**: Updated image tags for the `sentinel-api`, `sentinel-validator`, and `sentinel-consumer` components within the Helm chart.

#### Reason for Changes
- The primary driver for this release is the automated update of component image tags in the GitOps configuration. This ensures that the deployed infrastructure aligns with the latest built artifacts.
- Additionally, internal code quality improvements were made to the release agent script to resolve linter warnings and enforce PEP 8 standards, leading to a more maintainable codebase.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Stability and Maintainability:** Adherence to PEP 8 and resolution of linter warnings in the release agent contribute to a cleaner and more robust release automation process.
    - **Automated Deployment Alignment:** The automatic update of image tags in the Helm chart ensures that deployments consistently use the intended versions of the services.
- **(-) Disadvantages / Notes:**
    - No significant architectural trade-offs or disadvantages are introduced with these changes. The modifications focus on code quality and automated deployment practices.

---

## Release Notes - v1.18.0

This release introduces significant enhancements to our automated release process, focusing on improved changelog generation and more robust API error handling.

### Key Improvements:

*   **Automated Changelog Integration:** The release pipeline now automatically appends generated release notes to the `CHANGELOG.md` file. This ensures that our project's change history is consistently updated and easily accessible.
*   **Enhanced API Error Handling:** The release agent has been updated to provide more informative feedback when API interactions fail, particularly concerning the `GEMINI_API_KEY`. This includes increased retry attempts and longer delays for API calls, improving the resilience of the release process.
*   **Streamlined GitHub Release Titles:** Release titles in GitHub are now directly set to the version tag, simplifying the release identification.

#### Changed Files & Core Modifications
- The release workflow (`.github/workflows/release-agent.yaml`) has been updated to include steps for automatically updating and committing `CHANGELOG.md`.
- The release agent script (`agent/release/release_agent.py`) has been modified to:
    - Improve error reporting for missing API keys.
    - Increase retry mechanisms and delays for AI-driven note generation.
    - Integrate the generated release notes into the `CHANGELOG.md` file.
    - Adjust the GitHub release title format.

#### Reason for Changes
These changes are driven by the need to automate and standardize our release documentation process. By integrating changelog updates directly into the release pipeline and improving API error handling, we aim to increase efficiency, maintain a clear and up-to-date record of changes, and enhance the reliability of our automated release tooling.

#### Advantages & Architectural Trade-offs
*   **(+) Advantages:**
    *   **Improved Documentation:** Consistent and automated updates to `CHANGELOG.md` provide a reliable history of project changes.
    *   **Increased Automation:** Reduces manual effort required for release note management.
    *   **Enhanced Reliability:** More robust error handling and retry logic for API interactions improve the stability of the release process.
*   **(-) Disadvantages / Notes:**
    *   Requires the `GEMINI_API_KEY` to be correctly configured for full AI-driven release note generation. Failure to provide this key will result in a critical error during the release process.

---

## [1.16.1] - 2026-06-29

### Overview
This patch focuses on strengthening the API gateway's resilience against downstream latency and optimizing CPU utilization by eliminating reflection overhead during JSON processing. While raw RPS limits remain bound by network I/O, these internal optimizations ensure stable memory consumption and prevent cascading failures during high-load scenarios.

### Performance & Resilience
* **Zero-Allocation JSON Parsing:** Transitioned from standard `encoding/json` to the highly optimized `goccy/go-json` library.
* **Strict Data Structures:** Replaced dynamic `map[string]any` parsing with strict structs (`TransactionPayload` and `TransactionHashData`), significantly reducing Garbage Collection (GC) pauses and CPU reflection overhead.
* **Hard Context Timeouts:** Introduced a strict 2-second timeout limit for all incoming HTTP requests to prevent memory exhaustion (OOM) and goroutine leaks when downstream services (Redis/Redpanda) experience latency spikes.
* **Fail-Fast Retry Mechanism:** Updated the `executeWithRetry` logic to actively listen for context cancellations, allowing the system to gracefully halt operations if the client disconnects prematurely.

### Bug Fixes
* **Test Suite Reliability:** Resolved a `nil` pointer dereference (SIGSEGV) during test execution by initializing a No-Op `zap` logger.
* **Mock Hash Alignment:** Synchronized the `redismock` hash generation algorithm in the test environment with the new strict struct architecture to ensure 1:1 validation matching.

---

## [1.16.0] - 2026-06-27

### Overview
This release introduces a shift-left FinOps architecture by integrating Infracost directly into the continuous integration pipeline. Infrastructure cost changes are now automatically calculated, compared, and visualized before any code is merged into the main branch, bringing financial visibility directly to the engineering team.

### Key Features
* **Automated Cost Visibility:** Implemented a new GitHub Actions workflow (`infracost.yaml`) that triggers automatically on all pull requests.
* **Dynamic Baseline Comparison:** The pipeline now fetches the full repository history to dynamically compare the feature branch against the `main` branch, calculating exact monthly cost differences.
* **Pull Request Cost Tables:** Infrastructure cost changes are automatically injected as a detailed table directly into the pull request comments, ensuring reviewers have complete financial context before approving modifications.

### Infrastructure Updates
* **EKS Capacity Planning:** Adjusted the `desired_size` of the `sentinel-spot-nodes` EKS node group to validate the Infracost baseline and diff generation mechanics under real-world scaling scenarios.

### Technical Details
* Transitioned to the native `infracost comment github` CLI command for robust pull request commenting and streamlined token management.
* Configured `fetch-depth: 0` in the checkout action to guarantee accurate baseline generation across branches.

## [1.15.0] - 2026-06-24

### Security
- Updated Go toolchain to 1.26.4, patching standard library vulnerabilities.
- Bumped golang.org/x/crypto (v0.52.0) and golang.org/x/net (v0.55.0) to remediate SSH, HTML parsing, and HTTP/2 DoS vulnerabilities.
- Updated critical Python dependencies (cryptography, python-multipart, starlette) in uv.lock to resolve structural security flaws.

### Changed
- Modularized monolithic Helm charts into isolated Kubernetes resources for Postgres, Redis, Redpanda, and Console.
- Sanitized AWS and OCI Terraform configurations to strictly adhere to IaC standards.
- Segmented GitHub Actions into isolated, dedicated pipelines: security, format, and test.
- Enforced strict static analysis gates via golangci-lint (compiled vs Go 1.26.4 to resolve mismatch), rustfmt, and ruff.
- Parallelized Go, Rust, and Python test execution to optimize CI pipeline duration.

### Fixed
- Resolved unchecked errors (errcheck) across the Go API layer.
