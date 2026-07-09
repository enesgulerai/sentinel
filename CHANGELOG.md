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
