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
