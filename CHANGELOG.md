### v1.26.2

#### 🚀 Features & Core Modifications

*   **Enhanced API Throughput and Reduced Latency:** The Go API Gateway has been refactored for zero-allocation and optimized I/O operations. This includes aggressive tuning of Redis and Redpanda client configurations, reducing timeouts to sub-millisecond levels and increasing buffer sizes for higher throughput. The `ingestTransaction` handler now utilizes a sync pool for `TransactionPayload` to minimize memory allocations and garbage collection overhead.
*   **Streamlined CI/CD GitOps Updates:** The Continuous Deployment pipeline has been refactored to dynamically include registry and repository variables, making GitOps updates more robust and configurable.
*   **Improved Local Development Experience:** Taskfile commands have been streamlined for better readability and maintainability, simplifying local development workflows.
*   **AI-Driven Release Notes and Documentation:** Integrated AI agents for automated Semantic Versioning and release note generation, as well as for generating weekly architectural reviews based on git diffs.

#### 🛠 Stability & Performance (Fixes)

*   **Synchronized Redis Hashing in Tests:** Test suites have been updated to align Redis key hashing logic with the main payload structure, resolving inconsistencies.
*   **Resolved CI Deprecations and Test Suite Updates:** Addressed GolangCI-Lint's Node.js 20 deprecation and updated outdated test suites to ensure CI stability.
*   **API Stability Enhancements:** Introduced startup probes for the API, added a root endpoint for basic health checks, and increased context timeouts to improve overall API resilience.
*   **Chaos Mesh Test Stability:** Updated Chaos Mesh Helm deployment to use production values and synchronized Redis hash in tests to improve the stability of chaos engineering experiments.
*   **Validator and Consumer Component Updates:** Refactored validator and consumer components, along with load test fixtures, to align with the latest payload structures and improve data processing consistency.
*   **Local Deployment Configuration Updates:** Updated local deployment configurations and the task runner for a more stable local development environment.

#### 🏗 Architectural Impact

*   **Removed Legacy Jenkins Configuration:** Deprecated Jenkins CI configuration files have been removed, simplifying the CI/CD tooling landscape.
*   **Refined Helm Production Values:** Production Helm values have been updated to correctly specify image repositories for API, validator, and consumer components, ensuring correct deployment of production artifacts.
*   **Updated READMEs and Documentation:** Enhanced documentation for DevSecOps practices, including updated OPA policy rules and load testing readmes, providing clearer guidance on security and performance testing.
*   **Valkey Integration:** The `README.md` and related documentation now reflect the potential integration or compatibility with Valkey as a Redis alternative, indicating flexibility in datastore choices.

---

### v1.26.1

#### 🚀 Features & Core Modifications
- **Standardized Platform Engineering Workflows:** Migrated CI/CD pipelines from Jenkins to GitHub Actions. This centralizes workflow management and leverages a more integrated CI/CD ecosystem.
- **Automated Image Tagging and GitOps Updates:** Introduced a new GitHub Actions workflow (`cd-build-push.yaml`) that automatically builds and pushes Docker images to GHCR. It then updates the `values.production.yaml` file with the short Git SHA of the commit, ensuring GitOps manifests accurately reflect the deployed image versions.
- **Manual Triggering for CD Pipelines:** Added `workflow_dispatch` triggers to several GitHub Actions workflows, enabling manual execution of CI/CD pipelines for greater control over deployments.
- **Enhanced Policy Enforcement:** Introduced a new GitHub Actions workflow (`ci-opa-policy.yaml`) for validating Docker, Kubernetes, and AWS infrastructure configurations against Open Policy Agent (OPA) rules using `conftest`. This strengthens governance and compliance.

#### 🛠 Stability & Performance (Fixes)
- **OPA Explicit Versioning Compliance:** Modified base image tags in `values.yaml` to 'dev' to satisfy OPA's explicit versioning policy, ensuring better policy adherence.

#### 🏗 Architectural Impact
- **Jenkins Deprecation:** The `Jenkinsfile` has been removed, signifying a complete migration away from Jenkins for CI/CD.
- **New GitOps Deployment Strategy:** The `cd-build-push.yaml` workflow now directly manages updates to `values.production.yaml`, streamlining the GitOps deployment process.
- **Consolidated Policy Validation:** The OPA policy validation logic has been consolidated into a single workflow (`ci-opa-policy.yaml`), replacing the previous `sec-opa-policy.yaml`. This provides a unified approach to policy enforcement across different resource types.
- **Taskfile Enhancements:** The `Taskfile.yaml` has been updated with new Helm tasks (`helm:dev`, `helm:prod`) to differentiate between deploying local development images and production images tagged with Git SHAs. The `helm:off` task now handles the uninstallation of both development and production Helm releases.

---

# Release Notes - v1.26.0

This release focuses on enhancing security, refining the release automation process, and improving the accuracy of semantic versioning analysis.

## 🚀 Features & Core Modifications

*   **Strict Semantic Versioning Analysis:** The release agent now employs a strict, regex-based analysis of commit messages to determine semantic version bumps (MAJOR, MINOR, PATCH). This ensures more predictable and accurate versioning based on commit conventions.
*   **Enhanced Release Agent Automation:** The release agent's CI workflow has been optimized with a nightly schedule and smarter semantic versioning analysis. This streamlines the release process by automating checks and version determination.

## 🛠 Stability & Performance (Fixes)

*   **Dependency Security Updates:**
    *   The `cryptography` library has been updated to version `50.0.0`.
    *   The `gitpython` library has been updated to version `3.1.57`.
    These updates address high-severity vulnerabilities, significantly improving the security posture of the platform.

## 🏗 Architectural Impact

*   **Release Workflow Standardization:** CI workflows related to release processes have been standardized with consistent file naming conventions, improving maintainability and clarity of the automation infrastructure.
*   **Release Agent Triggering:** The release agent workflow is now triggered on a nightly schedule (`cron: '0 23 * * *'`) and via manual dispatch (`workflow_dispatch`), providing flexibility in release cadence and on-demand execution.

---

### v1.25.20

#### Changed Files & Core Modifications
- **Dockerfiles:** Modifications were made to the `Dockerfile` for the API, consumer, and validator services. These changes introduce BuildKit cache mounts for Go modules, Go build artifacts, Python virtual environment dependencies, and Rust build caches.

#### Reason for Changes
These changes were implemented to optimize the Docker image build process. By leveraging BuildKit's cache mount capabilities, we aim to significantly reduce the time required to build Docker images for our services. This is crucial for improving developer productivity and streamlining CI/CD pipelines.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Drastically Reduced Build Times:** Utilizing BuildKit cache mounts allows subsequent builds to reuse previously downloaded dependencies and compiled artifacts, leading to substantial time savings.
    - **Improved Developer Experience:** Faster build times mean quicker iteration cycles for developers.
    - **Efficient CI/CD:** Streamlined build processes contribute to more efficient and cost-effective continuous integration and continuous deployment pipelines.
- **(-) Disadvantages / Notes:**
    - This change relies on BuildKit being enabled and configured for Docker builds. While BuildKit is the default in recent Docker versions, older environments might require explicit configuration.

---

### v1.25.19

#### Changed Files & Core Modifications
- The CI workflow file `.github/workflows/chaos-test.yaml` was updated.
- The `kubectl port-forward` command within the chaos testing job was modified to target a deployment (`deploy/sentinel-api`) instead of a service (`svc/sentinel-api`).

#### Reason for Changes
- The chaos testing infrastructure was updated to directly target the API deployment for port-forwarding. This change ensures that the chaos tests are interacting with the actual running pods managed by the deployment, providing a more accurate simulation of real-world traffic patterns and potential failure scenarios. Previously, port-forwarding to the service might have bypassed certain aspects of the deployment's lifecycle or pod management.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Improved accuracy of chaos testing by directly targeting the deployment, leading to more realistic failure injection and resilience validation.
    - Enhanced debugging capabilities during chaos tests by ensuring the port-forward tunnel connects to the active pods managed by the deployment.
- **(-) Disadvantages / Notes:**
    - No significant architectural trade-offs are introduced. This is a refinement of the testing infrastructure.

---

### v1.25.18

#### Changed Files & Core Modifications
- **CI Configuration (`.github/workflows/chaos-test.yaml`):** The CI workflow for chaos testing has been updated. The `kubectl port-forward` command now targets the `sentinel-api` service directly within the `sentinel-namespace` instead of the ingress controller. The duration for establishing the port-forward tunnel has been increased, and the logs from the port-forward process are now captured and displayed.
- **Load Test Script (`tests/fixtures/loadtest.js`):** The duration of the k6 load test has been significantly reduced from 3 minutes to 30 seconds.

#### Reason for Changes
These changes are aimed at refining the chaos testing environment. By port-forwarding directly to the `sentinel-api` service, the test setup more accurately reflects direct service interaction under simulated failure conditions, rather than going through the ingress layer. The reduced k6 test duration allows for faster iteration and more frequent execution of chaos tests, improving the efficiency of identifying potential issues.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Test Isolation:** Targeting the API service directly provides a more focused test of its resilience and behavior under chaos, reducing dependencies on the ingress controller's stability during these specific tests.
    - **Faster Feedback Loop:** The reduced load test duration enables quicker execution of chaos tests, leading to faster identification and resolution of potential issues.
    - **Enhanced Debugging:** Capturing and displaying port-forward logs aids in diagnosing connectivity issues during chaos testing.
- **(-) Disadvantages / Notes:**
    - The previous chaos tests were implicitly testing the ingress controller's behavior under load. This change shifts the focus, and separate testing strategies may be needed to ensure the ingress controller's resilience is adequately covered.

---

### v1.25.17

#### Changed Files & Core Modifications
- **`.github/workflows/chaos-test.yaml`**: Modified the CI workflow for chaos testing. This update introduces the setup of a port-forwarding tunnel to the ingress controller before executing k6 load tests.

#### Reason for Changes
- To enable more accurate and reliable load testing scenarios within the chaos testing environment. Previously, direct access to the ingress controller for load testing might have been inconsistent or blocked, leading to unreliable test results.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Improved reliability and accuracy of chaos load tests by ensuring direct and stable access to the ingress controller.
    - Enhanced ability to simulate realistic traffic patterns under adverse conditions.
- **(-) Disadvantages / Notes:**
    - Introduces a slight overhead to the chaos test execution due to the port-forwarding setup and a short delay.
    - Requires the `ingress-nginx` namespace and the `ingress-nginx-controller` service to be available and accessible within the Kubernetes cluster for the chaos tests to run successfully.

---

### v1.25.16

#### Changed Files & Core Modifications
- Modified `tests/chaos/api-pod-kill.yaml` to correct a type mismatch in the `value` field within the pod kill manifest.

#### Reason for Changes
- A type mismatch was identified in the pod kill chaos experiment manifest. The `value` field, intended to represent a percentage, was incorrectly specified as an integer instead of a string. This could lead to unexpected behavior or failures in chaos testing scenarios.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Resolves a defect in the chaos testing framework, ensuring more reliable and accurate execution of pod kill experiments. This improves the overall stability and trustworthiness of our automated testing processes.
- **(-) Disadvantages / Notes:** None.

---

### v1.25.15

#### Changed Files & Core Modifications
- Modified the CI workflow file (`.github/workflows/chaos-test.yaml`) to correct a typo in a Kubernetes manifest filename reference.

#### Reason for Changes
- A typo in the CI configuration prevented the correct application of a chaos experiment manifest, specifically related to pod kill scenarios. This change ensures that the chaos testing infrastructure correctly references and applies all necessary experiment configurations.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Resolves a configuration error in the CI pipeline, ensuring the integrity and completeness of chaos testing. This improves the reliability of our automated testing by guaranteeing that all intended chaos experiments are executed.
- **(-) Disadvantages / Notes:** None. This is a minor correction to an existing test configuration.

---

### v1.25.14

#### Changed Files & Core Modifications
- The CI workflow file `.github/workflows/chaos-test.yaml` was updated.
- The change involves correcting the filename reference for a Kubernetes manifest used in the chaos testing workflow. Specifically, the manifest for the "pod kill" test has been updated from `api-gateway-pod-kill.yaml` to `api-pod-pod-kill.yaml`.

#### Reason for Changes
- This change addresses an inaccuracy in the chaos testing configuration. The previous filename did not correctly point to the intended chaos experiment, potentially leading to the wrong test being executed or the test failing due to a missing resource.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Ensures the chaos testing suite accurately targets the intended components for resilience testing, improving the reliability of our automated quality assurance processes. This leads to more robust deployments by validating failure scenarios correctly.
- **(-) Disadvantages / Notes:** No significant architectural trade-offs or negative impacts are introduced by this change. It is a configuration correction within the CI pipeline.

---

### v1.25.13

#### Changed Files & Core Modifications
- Modified Kubernetes manifests for network chaos experiments (`api-network-delay.yaml` and `redis-network-loss.yaml`).
- The `direction` field within the chaos experiment specifications has been updated from `both` to `to`.

#### Reason for Changes
- Corrected an invalid configuration in the network chaos manifests. The previous `both` direction setting was not correctly interpreted, leading to unintended behavior or failure in applying network disruptions as intended.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Ensures network chaos experiments are configured and executed with the intended directionality, improving the reliability and accuracy of chaos testing scenarios. This resolves a configuration defect, leading to more predictable test outcomes.
- **(-) Disadvantages / Notes:** No significant architectural trade-offs or disadvantages are introduced by this change.

---

### v1.25.12

#### Changed Files & Core Modifications
- The CI workflow for chaos testing (`.github/workflows/chaos-test.yaml`) has been updated. The Helm deployment step now bypasses the strict Helm `--wait` flag and instead utilizes a `kubectl wait` command to ensure all pods reach the `Ready` condition.

#### Reason for Changes
- This change addresses potential issues with Helm's strict waiting mechanism during CI deployments, particularly in complex environments where Horizontal Pod Autoscaler (HPA) might be involved. By switching to a direct `kubectl pod readiness check`, we ensure that the chaos tests proceed only after the application pods are fully operational, leading to more reliable test outcomes.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Improved reliability of chaos testing by ensuring deployments are fully ready before proceeding.
    - More robust handling of Kubernetes deployment states, especially when HPA is active.
- **(-) Disadvantages / Notes:**
    - This change is primarily within the CI/CD pipeline and does not directly impact the production application's runtime behavior. The timeout for pod readiness remains 10 minutes.

---

### v1.25.11

#### Changed Files & Core Modifications
- The `chaos-test.yaml` GitHub Actions workflow has been updated.
- New steps have been introduced to install and configure the Kubernetes Metrics Server within the chaos testing environment.

#### Reason for Changes
- The chaos testing environment experienced timeouts when waiting for Horizontal Pod Autoscalers (HPAs) to become ready. This was due to the absence of a functional Metrics Server, which is a prerequisite for HPAs to gather resource utilization data.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Resolves intermittent timeouts in the chaos testing pipeline, improving the reliability and stability of CI/CD for chaos-related deployments.
    - Enables proper functioning of Horizontal Pod Autoscalers within the chaos testing environment, allowing for more accurate simulation of dynamic scaling scenarios.
- **(-) Disadvantages / Notes:**
    - Introduces an additional dependency on the Metrics Server within the chaos testing infrastructure.
    - Requires the `metrics-server` to be deployed and configured correctly for the chaos testing environment to operate as expected.

---

### v1.25.10

#### Changed Files & Core Modifications
- **CI/CD Configuration (`.github/workflows/chaos-test.yaml`):** The Helm deployment process within the chaos testing workflow has been updated. This includes an increased timeout for Helm deployments and the addition of more detailed debug logging upon failure.

#### Reason for Changes
- These modifications were implemented to improve the reliability and diagnosability of the chaos testing environment. Increasing the deployment timeout addresses potential transient issues during Helm chart installations, while enhanced failure logging provides clearer insights when deployments do not succeed, aiding in faster troubleshooting.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Enhanced stability of the chaos testing pipeline by accommodating longer deployment times.
    - Improved debugging capabilities for deployment failures, leading to quicker resolution of CI/CD issues.
- **(-) Disadvantages / Notes:**
    - A longer timeout might slightly increase the overall execution time of the chaos test workflow in scenarios where deployments are slow.

---

### v1.25.9

#### Changed Files & Core Modifications
- **`.github/workflows/chaos-test.yaml`**: This file, which defines the CI workflow for chaos testing, has been significantly refactored. Key changes include:
    - **Chaos Mesh Installation**: Switched from a script-based installation to a Helm-based installation for Chaos Mesh. This provides better control over the Chaos Mesh deployment and its configuration.
    - **k6 Installation**: Modified the installation method for k6 from APT package management to a direct binary download. This aims to improve the speed and reliability of the CI pipeline.
    - **Concurrency Control**: Introduced concurrency settings to the workflow to prevent overlapping runs and improve resource management.
    - **Chaos Injection and Load Testing**: Adjusted the timing and execution of chaos injection and k6 load tests to ensure proper application of chaos experiments before load testing begins.

#### Reason for Changes
The primary motivation for these changes is to enhance the stability and speed of the chaos testing pipeline. By refactoring the workflow, we aim to achieve more reliable test execution and reduce the overall time spent in the CI process. The shift to Helm for Chaos Mesh installation and direct binary downloads for k6 are strategic decisions to streamline dependencies and improve deployment efficiency.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved CI Stability**: The Helm-based installation of Chaos Mesh offers a more robust and declarative approach, reducing potential installation failures.
    - **Faster CI Execution**: Direct binary downloads for k6 are generally faster and less prone to dependency issues compared to package managers, leading to quicker feedback loops.
    - **Enhanced Chaos Testing Reliability**: The adjustments in the workflow ensure that chaos experiments are properly applied and given sufficient time to take effect before load testing commences, leading to more accurate and meaningful test results.
    - **Better Resource Utilization**: Concurrency controls prevent redundant or conflicting workflow runs, optimizing resource usage.
- **(-) Disadvantages / Notes:**
    - **Helm Dependency**: The CI environment now requires Helm to be available for Chaos Mesh installation.
    - **Runtime Configuration**: The Chaos Mesh installation includes specific configurations (`chaosDaemon.runtime=containerd`, `chaosDaemon.socketPath=/run/containerd/containerd.sock`) which are tailored to the current environment. Any changes to the container runtime or its socket path in the cluster might require adjustments to this workflow.

---

### v1.25.8

#### Changed Files & Core Modifications
- The CI configuration for the chaos testing workflow (`.github/workflows/chaos-test.yaml`) has been updated. Specifically, the action used to set up the KinD Kubernetes cluster has been replaced, and the node image for the cluster has been updated.

#### Reason for Changes
- The previous `setup-kind` action was deprecated, leading to download errors (404). This change replaces the deprecated action with a maintained alternative to ensure the stability and reliability of the chaos testing environment.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Resolves a critical CI/CD pipeline failure by addressing a deprecated dependency, ensuring the continuity of chaos testing. This improves the robustness of our automated testing infrastructure.
- **(-) Disadvantages / Notes:** The change involves updating a core component of the CI infrastructure. While the new action is actively maintained, it's important to monitor its performance and compatibility in future releases. The specific `kindest/node` image version has also been updated, which may introduce subtle behavioral changes in the KinD cluster environment.

---

### v1.25.7

#### Changed Files & Core Modifications
- **`policy/aws_rules.rego`**: This file, which contains Open Policy Agent (OPA) rules for AWS governance, has been updated. The modifications focus on enhancing the logic for parsing and validating mandatory tags on AWS resources.

#### Reason for Changes
- The previous implementation exhibited inconsistencies in how it parsed Terraform-generated tags across different environments. This led to situations where resources correctly tagged in one environment might be flagged as non-compliant in another, undermining the reliability of our policy-as-code enforcement.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Policy Enforcement Accuracy:** The updated parsing logic ensures that mandatory tags are consistently and accurately identified across all environments, regardless of how Terraform structures them. This strengthens our zero-trust posture by ensuring critical metadata is always present.
    - **Reduced False Positives/Negatives:** By resolving parsing inconsistencies, this change minimizes the risk of incorrectly flagging compliant resources or missing non-compliant ones.
    - **Enhanced Governance:** Provides a more robust and reliable mechanism for enforcing organizational tagging standards, which is crucial for cost allocation, security auditing, and resource management.
- **(-) Disadvantages / Notes:**
    - No direct disadvantages or architectural trade-offs are introduced by this change. The modifications are purely focused on improving the accuracy and reliability of existing policy enforcement.

---

### v1.25.6

#### Changed Files & Core Modifications
- `policy/aws_rules.rego`: Modified the `has_tag` helper function to implement a deep recursive search for tags within AWS resources. This change enhances the policy engine's ability to correctly identify mandatory tags, even when they are nested within complex or inconsistently structured HCL (HashiCorp Configuration Language) data.

#### Reason for Changes
- The previous implementation of the tag checking logic in Conftest's HCL parser was encountering issues with certain Terraform configurations. This resulted in mandatory tags not being correctly identified, leading to potential policy violations being missed. The update addresses these parser bugs by introducing a more robust and recursive method for tag discovery.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Policy Enforcement:** Ensures that mandatory tags are consistently and accurately detected across a wider range of Terraform configurations, strengthening governance and compliance.
    - **Enhanced Robustness:** The recursive search mechanism makes the policy engine more resilient to variations in how tags are defined in the infrastructure-as-code.
- **(-) Disadvantages / Notes:**
    - This change is a workaround for specific limitations within the Conftest HCL parser. Future updates to Conftest or its HCL parsing library may allow for a simpler implementation.

---

### v1.25.5

#### Changed Files & Core Modifications
- **Policy Definition (`policy/aws_rules.rego`):** The tag validation logic within the AWS policy rules has been enhanced. This modification ensures that the policy engine can correctly interpret and validate resource tags regardless of whether they are provided as a direct object or an array of key-value pairs.
- **Configuration Files:** Renamed several YAML configuration files (`Taskfile.yml`, `docker-compose.yml`, `docker/jenkins/docker-compose.yml`) to their `.yaml` extension for consistency.

#### Reason for Changes
The tag validation rule in the AWS policy was updated to accommodate different formats in which resource tags might be parsed by the policy evaluation tool. This ensures more robust and accurate policy enforcement across various AWS resource configurations.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Increased policy enforcement accuracy and reliability by supporting a wider range of tag formats. This reduces the likelihood of false positives or negatives in policy evaluations, leading to better security and compliance posture.
- **(-) Disadvantages / Notes:** No significant architectural trade-offs or disadvantages are introduced by this change. The renaming of configuration files is a minor organizational improvement.

---

### v1.25.4

#### Changed Files & Core Modifications
- **CI/CD Pipeline (`.github/workflows/infracost.yaml`):** The Infracost analysis output format within the GitHub Actions workflow has been updated from HTML to a plain text table. This change affects how cost estimation results are presented in the CI/CD summary.
- **Policy as Code (`policy/aws_rules.rego`):** Introduced a new helper function `has_tag` to robustly handle the parsing of resource tags, accommodating variations in how Conftest might represent them (as an object or an array of objects). This enhances the reliability of tag-based governance rules.

#### Reason for Changes
- **Improved CI/CD Visibility:** The modification to the Infracost output format aims to provide a more direct and easily digestible cost breakdown within the GitHub Actions summary, improving developer visibility into infrastructure costs during the development lifecycle.
- **Enhanced Tagging Enforcement:** The update to the AWS tagging policy addresses inconsistencies in tag parsing, ensuring more reliable enforcement of mandatory tags across AWS resources. This strengthens governance and compliance by accurately identifying resources missing required metadata.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Enhanced Developer Experience:** The plain text table format for Infracost output in CI/CD summaries offers immediate clarity on cost implications without requiring users to open separate reports.
    - **Increased Policy Robustness:** The `has_tag` helper function makes the tag enforcement policy more resilient to variations in input data, reducing false negatives and improving the overall effectiveness of governance.
    - **Improved Governance and Compliance:** More reliable tag enforcement leads to better resource organization, cost allocation, and security posture.
- **(-) Disadvantages / Notes:**
    - The previous HTML report format for Infracost is no longer generated directly in the GitHub Summary. If detailed HTML reports are required, they would need to be configured separately.

---

### v1.25.3

#### Changed Files & Core Modifications
- **CI/CD Pipeline (`.github/workflows/infracost.yaml`):** The Infracost analysis workflow has been updated to generate an HTML report for the GitHub Step Summary, replacing the previous Markdown format. This change aims to improve the readability and presentation of cost analysis results within the CI/CD process.
- **Infrastructure Configuration (`infrastructure/terraform/aws-finops-mock/eks.tf`, `infrastructure/terraform/aws-finops-mock/network.tf`):** Environment tags for EKS cluster and VPC resources have been standardized to lowercase "production". This ensures consistency in environment labeling across infrastructure components.
- **API Dependencies (`src/api/go.mod`, `src/api/go.sum`):** Updated AWS SDK for Go v2 dependencies. This includes explicit inclusion of `aws-sdk-go-v2`, `config`, `credentials`, and `s3` as direct requirements, while also updating the `golang.org/x/text` dependency. These updates are likely to incorporate the latest features, security patches, or bug fixes from the AWS SDK.

#### Reason for Changes
This release addresses issues identified in CI workflows related to validation and security failures. Specifically, the Infracost reporting format was updated for better visibility, and infrastructure resource tagging was standardized for improved environment management. The dependency updates in the API are part of ongoing maintenance to ensure the use of current and secure libraries.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Enhanced visibility and clarity of cost analysis reports within CI/CD through HTML formatting.
    - Improved consistency in infrastructure environment tagging, aiding in better resource management and automation.
    - Updated AWS SDK dependencies may bring performance improvements, new features, and critical security patches to the API.
- **(-) Disadvantages / Notes:**
    - The change in Infracost report format might require minor adjustments in any downstream tooling or processes that parse the GitHub Step Summary.
    - Updating SDKs can sometimes introduce subtle behavioral changes, though these are typically well-tested.

---

### v1.25.2

#### Changed Files & Core Modifications

*   **CI/CD Workflow Enhancements:** Several GitHub Actions workflows have been updated to improve clarity and functionality. This includes renaming workflows for better categorization (e.g., `CI: Code Quality & Formatting`, `CI: Infracost FinOps Check`, `CD: Release Agent`, `CI: Security Code Scanning`, `CI: Application Unit Tests`).
*   **Infracost FinOps Check Workflow:** The `infracost.yaml` workflow has been significantly modified. It now triggers on pushes to the `main` branch and includes `workflow_dispatch` for manual runs. The permissions have been adjusted to `contents: read`. The output has been enhanced to print standard breakdown logs and generate a GitHub Step Summary report for cost estimations.
*   **Chaos Engineering Documentation:** The `tests/chaos/README.md` file has been updated to include details about the automated CI pipeline for chaos scenarios, new chaos experiment scenarios (CPU Stress, Redis Network Loss), and refined instructions for prerequisites, installation, execution, and cleanup.

#### Reason for Changes

These changes are driven by the need to enhance our continuous integration and delivery pipelines, improve cost visibility, and strengthen our chaos engineering practices.

*   The renaming of CI/CD workflows provides better organization and immediate understanding of each pipeline's purpose.
*   The enhancements to the Infracost workflow aim to provide more actionable cost insights directly within the CI process, enabling better FinOps practices. Triggering on `main` branch pushes and adding `workflow_dispatch` allows for more flexible and timely cost analysis. The output to GitHub Step Summary makes cost reports more accessible.
*   The updates to the Chaos Engineering documentation aim to provide a more comprehensive guide for users and to reflect the automation of these tests within the CI pipeline, ensuring regular validation of system resilience.

#### Advantages & Architectural Trade-offs

*   **(+) Advantages:**
    *   **Improved CI/CD Clarity:** Workflow renames make the purpose of each pipeline immediately clear.
    *   **Enhanced FinOps Visibility:** The Infracost workflow now provides more integrated and accessible cost estimations, aiding in financial governance.
    *   **Automated Resilience Testing:** The documentation now clearly outlines the automated CI pipeline for chaos engineering, ensuring regular validation of system stability.
    *   **Expanded Chaos Engineering Scenarios:** The addition of new scenarios (CPU Stress, Redis Network Loss) allows for more thorough testing of system resilience under various failure conditions.
    *   **Streamlined Chaos Engineering Documentation:** Updated instructions simplify the setup and execution of chaos experiments.
*   **(-) Disadvantages / Notes:**
    *   The Infracost workflow now requires `contents: read` permissions.
    *   Manual execution of chaos scenarios still requires the installation of Chaos Mesh and its CRDs in the Kubernetes cluster.

---

### v1.25.1

#### Changed Files & Core Modifications
- **New CI/CD Workflows:** Introduced two new GitHub Actions workflows:
    - `chaos-test.yaml`: Automates nightly chaos engineering experiments, including load testing with Chaos Mesh for stress, network delay, pod kill, and network loss scenarios.
    - `opa-policy.yaml`: Implements automated Open Policy Agent (OPA) governance checks using Conftest for Docker, Kubernetes (Helm templates), and AWS Terraform configurations.
- **Removed Redundant Security Scan:** The `scan-helm-conftest` job within `security.yaml` has been removed as its functionality is now covered by the new `opa-policy.yaml` workflow.
- **Chaos Experiment Definitions:** Added new YAML files defining specific chaos injection experiments (e.g., `api-cpu-stress.yaml`, `api-network-delay.yaml`, `api-pod-kill.yaml`, `redis-network-loss.yaml`).

#### Reason for Changes
These changes are driven by the need to enhance system resilience and enforce governance policies through automation. The introduction of chaos engineering aims to proactively identify and address potential failure points under simulated adverse conditions. The OPA policy validation ensures that infrastructure and application configurations adhere to predefined security and compliance standards before deployment.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Resilience:** Proactive identification of system weaknesses through automated chaos engineering.
    - **Enhanced Security & Compliance:** Automated enforcement of governance policies across container, orchestration, and cloud resources.
    - **Increased CI/CD Efficiency:** Integration of governance and resilience testing directly into the CI/CD pipeline, reducing manual effort and lead time.
    - **Better Observability:** Chaos experiments can provide valuable insights into system behavior under stress.
- **(-) Disadvantages / Notes:**
    - **Increased CI/CD Complexity:** The addition of new workflows and tools may require a learning curve for the team.
    - **Resource Consumption:** Running chaos experiments and policy validations consumes CI/CD runner resources.
    - **Potential for False Positives/Negatives:** Tuning of chaos experiments and OPA policies will be crucial to minimize noise and ensure effectiveness.

---

### v1.25.0

#### Changed Files & Core Modifications
- **Policy Enforcement:** Introduced comprehensive policy-as-code rules across AWS, Kubernetes, and Docker environments. This includes updates to `aws_rules.rego`, `docker_rules.rego`, and `k8s_rules.rego`.
- **Infrastructure as Code:** Modified Helm chart values (`sentinel/values.yaml`) and Kubernetes deployment templates (e.g., `api-deployment.yaml`, `consumer-deployment.yaml`, etc.) to incorporate standardized labels. Terraform configurations (`eks.tf`, `network.tf`, `localstack.tf`) were updated to enforce these same tagging standards on AWS resources.
- **CI/CD Pipeline:** Updated the `Dockerfile` for the Jenkins image to use a multi-stage build process for improved efficiency and security.

#### Reason for Changes
This release significantly enhances the project's governance and security posture by implementing strict, enterprise-wide policies. The core objective is to enforce a unified standard for security, cost management (FinOps), and operational reliability across all cloud and containerized components. This addresses the need for automated policy enforcement to prevent misconfigurations, reduce operational overhead, and ensure compliance with best practices.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Enhanced Security:** Stricter policies on network exposure, IAM privileges, and container execution (non-root, no privileged pods) significantly reduce the attack surface and blast radius of potential compromises.
    - **Improved FinOps:** Mandatory tagging and optimized resource configurations (e.g., Graviton instances, SPOT capacity, gp3 volumes) provide better cost visibility and control, leading to substantial cost savings.
    - **Increased Reliability & Performance:** Enforcing resource requests and avoiding CPU limits in Kubernetes deployments ensures better scheduling and prevents performance degradation due to throttling.
    - **Supply Chain Security:** Mandating explicit image tags and multi-stage Docker builds reduces the risk of unexpected changes and minimizes image attack surfaces.
    - **Automated Governance:** Policy-as-code provides immediate feedback during development and CI/CD, shifting security and compliance left and reducing manual review burdens.
- **(-) Disadvantages / Notes:**
    - **Infrastructure Updates:** Existing infrastructure and deployments may require adjustments to comply with the new tagging and resource configuration policies.
    - **Build Process Optimization:** The Jenkins Dockerfile update introduces a multi-stage build, which is a best practice for image size and security but requires understanding the new build stages.
    - **Policy Adherence:** Continuous monitoring and potential adjustments to policies will be necessary as the cloud environment and threat landscape evolve.

---

### v1.24.7

#### Changed Files & Core Modifications

*   **CI/CD Workflows (`.github/workflows/`):** Significant updates across multiple CI pipelines (`format.yaml`, `release-agent.yaml`, `security.yaml`, `test.yaml`). These include:
    *   Refactoring the release agent script for improved execution and dependency management using `uv`.
    *   Optimizing pipeline performance through enhanced caching strategies (e.g., TFLint plugins, Rust dependencies).
    *   Strengthening security boundaries by adjusting permissions and integrating security scanning tools more effectively.
    *   Introducing `paths-ignore` to exclude documentation changes from triggering code quality and test pipelines, improving efficiency.
    *   Standardizing the setup of Python environments using `astral-sh/setup-uv@v5` for consistency and performance.
    *   Modifying the `conftest` installation method for better reliability.
    *   Updating the `gosec` and `govulncheck` integration within the security pipeline.

#### Reason for Changes

These changes were driven by a need to enhance the efficiency, reliability, and security of our continuous integration and deployment processes. Specifically, the refactoring of the release agent script addresses issues with its execution and ensures proper dependency handling. Optimizations in pipeline performance, caching, and security boundaries are aimed at reducing execution times, minimizing resource consumption, and strengthening our security posture. The exclusion of documentation changes from certain pipelines streamlines the development workflow by preventing unnecessary pipeline runs.

#### Advantages & Architectural Trade-offs

*   **(+) Advantages:**
    *   **Improved CI/CD Performance:** Enhanced caching and optimized workflow configurations lead to faster pipeline execution times.
    *   **Increased Reliability:** Refactored scripts and standardized environment setups reduce the likelihood of CI/CD failures.
    *   **Enhanced Security:** More robust integration of security scanning tools and refined workflow permissions strengthen the overall security posture.
    *   **Developer Efficiency:** Ignoring documentation changes in core pipelines allows developers to iterate faster without triggering lengthy checks for non-code modifications.
    *   **Modernized Tooling:** Adoption of `uv` for Python dependency management brings performance benefits and a more streamlined experience.
*   **(-) Disadvantages / Notes:**
    *   No significant architectural trade-offs or disadvantages are introduced. The changes focus on improving existing processes and tooling.

---

### v1.24.6

#### Changed Files & Core Modifications
- **CI/CD Pipeline Enhancements:** Introduced a new `format-terraform` job in the `.github/workflows/format.yaml` to automate Terraform formatting and linting. This includes setting up Terraform and TFLint within the CI environment.
- **Pre-commit Hook Integration:** Updated `.pre-commit-config.yaml` to incorporate native local hooks for Rust and Terraform. This replaces previous Go-specific hooks and adds `cargo fmt`, `cargo clippy`, `terraform fmt`, and `tflint` to the local development workflow.
- **Terraform Configuration:** Added a new `.tflint.hcl` file to define TFLint configuration, including enabling the AWS provider and specific rules.
- **Terraform Code Adjustments:** Minor formatting and whitespace adjustments were made across various Terraform files (`eks.tf`, `network.tf`, `main.tf`, `provider.tf`) to align with new formatting standards and ensure consistency.
- **Terraform Version Pinning:** Explicitly set `required_version = ">= 1.5.0"` in `main.tf` and `provider.tf` for the Localstack and OCI configurations, respectively, to enforce a minimum Terraform version.

#### Reason for Changes
This release focuses on improving the development workflow and ensuring code quality for infrastructure as code. The integration of TFLint and native pre-commit hooks for Terraform and Rust aims to catch formatting and linting issues earlier in the development cycle, reducing the likelihood of errors reaching production. Standardizing Terraform formatting and enforcing minimum versions also contributes to a more robust and maintainable infrastructure codebase.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Enhanced code quality and consistency for Terraform and Rust code through automated formatting and linting.
    - Earlier detection of potential infrastructure misconfigurations and style violations.
    - Improved developer experience by providing immediate feedback on code quality during local development.
    - Reduced technical debt by enforcing standards and best practices.
    - Increased reliability of infrastructure deployments by catching issues before they are committed.
- **(-) Disadvantages / Notes:**
    - Developers will need to ensure their local environments are set up to run these new pre-commit hooks.
    - The introduction of TFLint may surface new linting rules that require attention in existing Terraform code.

---

### v1.24.5

#### Changed Files & Core Modifications
- **`README.md`**: Updated documentation to include instructions for running load tests and added a new section for local AWS simulation.
- **`Taskfile.yml`**: Modified Docker build process to include `--build` for `docker:on`, updated the pre-pulling message to reflect the `valkey` image, and streamlined `helm:forward` by removing the console port-forward.
- **`docker/consumer/requirements.txt`**: Removed OpenTelemetry dependencies.
- **`docker/validator/Dockerfile`**: Optimized the build process by switching to an Alpine-based Rust image and using `apk` for package management, resulting in a smaller image size.
- **`infrastructure/helm/README.md`**: Updated the estimated container sizes for the Go API and Rust Validator, and refined instructions for patching the metrics server for local development.
- **`src/api/main.go`**: Refactored the AWS S3 audit logging to use a buffered channel and a pool of worker goroutines for asynchronous processing, improving API responsiveness and throughput.
- **`src/inference/consumer.py`**: Enhanced cross-platform compatibility by conditionally installing `uvloop` and added a check for Windows environments. Also updated the default database connection string to use `sentinel_user`.
- **`tests/README.md`**: Updated the load testing tool from `oha` to `k6`.

#### Reason for Changes
This release focuses on enhancing system performance, reliability, and developer experience. Key drivers include:
- **API Concurrency and Throughput:** Optimizing the asynchronous processing of audit logs to the S3 bucket is critical for maintaining low API latency under high load.
- **Cross-Platform Compatibility:** Ensuring the system functions correctly across different operating systems, particularly for development and testing environments.
- **Image Optimization:** Reducing container image sizes for faster deployments and lower resource consumption.
- **Documentation and Tooling:** Improving developer workflows by updating documentation and load testing tools.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved API Latency and Throughput:** The asynchronous S3 audit log processing via a worker pool significantly reduces the impact of I/O operations on API request handling, allowing for higher concurrent throughput.
    - **Reduced Container Footprint:** The optimized `validator` Docker image is substantially smaller, leading to faster deployments and reduced storage requirements.
    - **Enhanced Cross-Platform Support:** The conditional `uvloop` installation and Windows detection improve the reliability of the inference consumer across various development and deployment environments.
    - **Streamlined Local Development:** Simplifying the `helm:forward` task by removing unnecessary port-forwarding configurations.
    - **Modernized Load Testing:** Integration of `k6` provides a more robust and feature-rich load testing framework.
    - **Improved Developer Workflow:** Clearer documentation for load testing and local AWS simulation facilitates easier setup and verification.
- **(-) Disadvantages / Notes:**
    - The new S3 audit logging mechanism introduces a buffered channel (`s3TaskQueue`) with a capacity of 50,000 tasks. If this buffer becomes full, audit logs will be dropped to maintain API performance. Monitoring of this queue size and worker utilization is recommended.
    - The removal of OpenTelemetry dependencies from the consumer may impact distributed tracing capabilities for that specific component.
    - The default database user in the consumer has been updated to `sentinel_user`, requiring potential configuration adjustments in environments using the previous default.

---

### v1.24.4

#### Changed Files & Core Modifications
- Modified `src/api/main.go` to update the AWS SDK configuration for local development environments. The previous custom endpoint resolver has been replaced with the `config.WithBaseEndpoint` option.

#### Reason for Changes
- The previous implementation used a deprecated method for resolving AWS endpoints, which was flagged by `golangci-lint`. This change addresses the linting issue by adopting the current recommended approach for configuring custom endpoints, particularly relevant for local development with tools like LocalStack.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:** Resolves a technical debt by updating to a supported AWS SDK configuration method, ensuring continued compatibility and adherence to best practices. This maintains the ability to easily test against local AWS-compatible services.
- **(-) Disadvantages / Notes:** No significant architectural trade-offs or performance impacts are expected. This is a maintenance update focused on code quality and compatibility.

---

### v1.24.3

#### Changed Files & Core Modifications
- **`infrastructure/helm/sentinel/templates/localstack/localstack.yaml`**: Resource requests for the LocalStack container have been moved from the `image` section to the `resources` section.
- **`src/api/main.go`**: Added a nil check for the S3 client before attempting to write audit logs.

#### Reason for Changes
The primary driver for these changes is to resolve intermittent CI pipeline failures observed in tests and conftest policies. Specifically, the failures were related to the LocalStack environment and the audit logging mechanism.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved CI Stability:** Resolving the CI pipeline failures enhances the reliability and stability of our continuous integration process.
    - **Robust Audit Logging:** The addition of a nil check for the S3 client in `main.go` prevents potential panics in test environments where the S3 client might not be initialized, ensuring more predictable behavior.
    - **Clearer Resource Management:** Moving LocalStack resource requests to the dedicated `resources` block in the Helm chart improves clarity and adherence to Kubernetes best practices for resource definition.
- **(-) Disadvantages / Notes:**
    - No significant disadvantages or architectural trade-offs are introduced by these changes. The modifications are focused on stability and correctness.

---

### v1.24.2

#### Changed Files & Core Modifications

*   **Dependency Updates:** The `gitpython` library has been updated to version `3.1.55` (from `3.1.50`). This addresses security vulnerabilities and ensures the use of a more stable and secure version.
*   **Kubernetes Resource Definitions:** The Helm chart for `localstack` has been updated to include Kubernetes labels (`env: local`) and resource requests (`cpu: "250m"`, `memory: "256Mi"`) for the `localstack` container.

#### Reason for Changes

This release addresses two key areas:

1.  **Security Vulnerabilities:** An update to `gitpython` was necessary to mitigate known security vulnerabilities within the library.
2.  **Kubernetes Resource Management:** The addition of Kubernetes labels and resource requests to the `localstack` deployment improves the manageability and observability of this component within a Kubernetes environment. Specifically, the `env: local` label aids in environment identification, and resource requests help Kubernetes with scheduling and resource allocation.

#### Advantages & Architectural Trade-offs

*   **(+) Advantages:**
    *   Enhanced security posture by resolving `gitpython` vulnerabilities.
    *   Improved Kubernetes resource management and scheduling for the `localstack` service.
    *   Better clarity and organization within Kubernetes deployments due to the addition of environment labels.
*   **(-) Disadvantages / Notes:**
    *   The addition of resource requests for `localstack` may require adjustments to cluster resource quotas or limits if not already provisioned.

---

### v1.24.1

#### Changed Files & Core Modifications
- **Documentation:** Updated architecture diagrams to reflect the current system flow and added comprehensive documentation for the LocalStack Terraform setup.
- **Helm Charts:** Updated deployment configurations for the `api`, `validator`, and `consumer` services to reference the latest image tag (`58ede6b`).
- **Terraform Configuration:** Introduced a new Terraform module for LocalStack, defining the S3 bucket for audit logs and enabling versioning. This replaces the previous SQS queue definition.

#### Reason for Changes
This release focuses on improving the clarity and maintainability of the project's infrastructure and documentation. The architectural diagrams have been refreshed to provide a more accurate representation of the system's event-driven flow. Furthermore, the local development environment has been enhanced by formalizing the LocalStack S3 infrastructure setup using Terraform, ensuring consistency and ease of deployment for local testing. The update to the Helm charts ensures that all deployed components are running the latest specified image.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Enhanced clarity of system architecture through updated diagrams.
    - Improved local development experience with a robust and documented LocalStack setup.
    - Increased reliability and consistency in infrastructure provisioning via Terraform.
    - Ensured all services are deployed with the latest specified image tag.
- **(-) Disadvantages / Notes:**
    - The removal of the SQS queue definition in the LocalStack Terraform configuration implies a shift in how certain inter-service communication or data handling might be managed locally. Users should verify if this impacts any local testing workflows that relied on the SQS queue.

---

### v1.24.0

#### Changed Files & Core Modifications
- **Infrastructure (Helm & Terraform):** Introduced new Kubernetes Deployments and Services for LocalStack, enabling a local cloud environment. Configured Terraform to manage LocalStack resources, including S3 buckets and SQS queues.
- **API Deployment Configuration:** Modified the API's Kubernetes deployment to include an `AWS_ENDPOINT_URL` environment variable, allowing it to target the LocalStack instance within the cluster.
- **API Application Code:**
    - Updated `go.mod` and `go.sum` to include new AWS SDK v2 dependencies required for S3 integration.
    - Modified `main.go` to initialize an AWS S3 client, with dynamic configuration for either production AWS or LocalStack endpoints.
    - Implemented asynchronous S3 audit logging for incoming transactions within the `ingestTransaction` function, executed in a separate goroutine.
    - Updated the application version string to "1.17.0-cloud-native".

#### Reason for Changes
This release focuses on enhancing the development and testing experience by introducing robust local cloud emulation capabilities. The primary drivers are:
- **Improved Developer Productivity:** Enabling developers to run and test cloud-native services, specifically S3 interactions, locally without relying on external AWS credentials or incurring costs.
- **Streamlined CI/CD:** Facilitating more comprehensive integration testing within CI pipelines by providing a consistent and isolated cloud environment.
- **Enhanced Observability:** Implementing asynchronous S3 audit logging for all transactions to provide a persistent and auditable record, decoupled from the primary request path to maintain high throughput.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Local Development & Testing:** Significantly improves the developer workflow by allowing local execution and testing of S3-dependent features using LocalStack.
    - **Cost Reduction:** Eliminates the need for actual AWS S3 calls during local development and potentially in CI environments, reducing operational costs.
    - **Faster Feedback Loops:** Enables quicker iteration and testing cycles for features interacting with S3.
    - **Decoupled Audit Logging:** Asynchronous S3 audit logging ensures that the primary API request latency and throughput remain unaffected, as the logging operation is non-blocking.
    - **Production Readiness:** The S3 client initialization is designed to seamlessly switch between LocalStack and production AWS endpoints based on the `AWS_ENDPOINT_URL` configuration.
- **(-) Disadvantages / Notes:**
    - **Infrastructure Complexity:** Introduces new infrastructure components (LocalStack deployment and service) that require management and monitoring.
    - **LocalStack Consistency:** While powerful, LocalStack may not perfectly replicate all AWS S3 behaviors. Thorough testing against actual AWS services is still recommended before production deployment.
    - **Increased Dependency Management:** The inclusion of AWS SDK v2 dependencies adds to the project's dependency footprint.

---

### v1.23.0

#### Changed Files & Core Modifications
- **Infrastructure Documentation:** Updated `README.md` files within the `infrastructure/helm` and `tests/chaos` directories.
- **Chaos Engineering:** Introduced new Chaos Mesh experiment definitions (`api-pod-kill.yaml`, `api-network-delay.yaml`) and their corresponding documentation.
- **Network & Observability:** Integrated documentation and instructions for replacing `kube-proxy` with Cilium (eBPF) and enabling the Hubble UI.

#### Reason for Changes
This release focuses on enhancing the robustness and performance of the Sentinel project through two key initiatives:

1.  **Chaos Engineering:** To proactively identify and address potential failure points, we've introduced a suite of chaos engineering experiments. These experiments are designed to test the system's resilience, self-healing capabilities, and fault tolerance under various simulated failure conditions.
2.  **Network Performance Optimization:** To significantly improve network throughput and reduce latency, we are transitioning to an eBPF-based networking solution using Cilium. This architectural shift aims to eliminate network bottlenecks, especially under high load, and provide enhanced observability through Hubble.

#### Advantages & Architectural Trade-offs
-   **(+) Advantages:**
    *   **Enhanced Resilience:** Chaos engineering experiments allow for early detection and mitigation of vulnerabilities, leading to a more stable and reliable system.
    *   **Improved Network Performance:** Replacing `kube-proxy` with Cilium (eBPF) offers substantial reductions in network latency and increased throughput by performing network routing directly within the Linux kernel. This also ensures consistent $O(1)$ routing performance.
    *   **Advanced Observability:** The integration of Hubble provides zero-instrumentation, real-time service mapping and traffic analysis, offering deep insights into microservice communication.
    *   **Scalability:** The eBPF-based networking is better equipped to handle high RPS loads without CPU bottlenecks.
-   **(-) Disadvantages / Notes:**
    *   **Infrastructure Requirement:** The adoption of Cilium requires enabling `kube-proxy` replacement during Helm installation.
    *   **Pod Restart:** After installing or upgrading Cilium, existing pods in the `sentinel-namespace` will need to be restarted to adopt the new CNI and receive updated IP addresses.
    *   **Chaos Mesh Dependency:** Running chaos experiments requires the installation of Chaos Mesh.

---

### v1.22.0

#### Changed Files & Core Modifications
- **New Agent for Architectural Reviews:** Introduced a new `agent/doc` directory containing `doc_agent.py` and `README.md`. This agent is responsible for generating weekly architectural review reports.
- **Enhanced Release Agent:** Modified `agent/release/release_agent.py` to incorporate dynamic persona assignment and integrate with the new "Engineering Council" concept for release note generation.
- **Configuration Updates:**
    - `.env.example` now includes `GEMINI_API_KEY` for AI integration.
    - `.gitignore` has been updated to exclude AI-generated reports.
    - `Taskfile.yml` now includes tasks for running both the `doc` and `release` agents.
    - `README.md` has been updated to document the new AI agents.
- **Dependency Updates:** `pyproject.toml` and `uv.lock` now include `google-genai` and related dependencies.

#### Reason for Changes
This release introduces significant advancements in the automation of engineering processes, specifically focusing on improving release management and architectural oversight. The primary drivers are:

1.  **Automated Release Notes Generation:** To streamline the release process, an AI-powered agent has been enhanced to automatically generate structured release notes based on commit messages and code diffs. This agent now leverages dynamic personas to provide more contextually relevant and domain-specific analysis.
2.  **Proactive Architectural Review:** A new "Autonomous Engineering Council" (Doc Agent) has been established to provide regular, persona-driven architectural reviews. This agent analyzes code changes over a defined period to identify potential issues, track progress, and ensure architectural alignment, thereby reducing technical debt and improving overall system quality.
3.  **Enhanced Developer Experience (DevEx):** By automating these critical but time-consuming tasks, developers can focus more on core development, leading to increased productivity and faster iteration cycles. The fail-fast mechanisms and clear error reporting for missing configurations (like API keys) also improve the onboarding and operational experience.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Automated & Consistent Release Notes:** Ensures timely and structured release notes, reducing manual effort and potential for human error.
    - **Proactive Architectural Governance:** The Doc Agent provides continuous, AI-driven oversight, identifying potential architectural drift and technical debt early.
    - **Dynamic Persona Analysis:** Both agents leverage AI to adopt relevant expert roles, leading to more insightful and targeted analysis for release notes and architectural reviews.
    - **Improved DevEx:** Simplifies complex tasks like versioning and documentation generation, allowing engineers to focus on feature development.
    - **Reduced Hallucinations:** Implemented stricter AI constraints and fail-fast mechanisms to ensure reliable and actionable outputs.
- **(-) Disadvantages / Notes:**
    - **External API Dependency:** The functionality of these agents is dependent on the availability and performance of the Gemini API.
    - **Configuration Requirement:** Requires the `GEMINI_API_KEY` to be set in the environment, which needs to be managed securely.
    - **Potential for AI Misinterpretation:** While efforts have been made to mitigate hallucinations, AI-generated content may still require human review for critical decisions.
    - **Increased Operational Overhead:** Running these agents introduces new tasks and potential points of failure that need to be monitored.

---

### v1.21.4

#### Changed Files & Core Modifications
- **Documentation Overhaul:** Significant updates to the `README.md` files across the `core`, `agent/release`, and `policy` directories.
- **Performance Benchmarks:** Introduction of new images and updated text in `README.md` to reflect peak performance metrics.
- **AWS FinOps Simulation:** Updated `README.md` for the AWS FinOps Terraform module, including new cost reduction figures and revised optimization strategies.
- **Policy-as-Code Documentation:** New `README.md` for the `policy` directory, detailing OPA/Rego rules for infrastructure, container, and Kubernetes governance.
- **AI Release Agent Documentation:** New `README.md` for the `agent/release` directory, outlining the functionality and usage of the AI-driven release automation.
- **Image Updates:** Reorganization and addition of new images related to performance benchmarks and cost analysis reports.

#### Reason for Changes
This release focuses on enhancing the project's documentation and introducing new capabilities for automated release management and policy enforcement. The goal is to provide clearer guidance on system performance, cost optimization strategies, and robust security/governance practices.

#### Advantages & Architectural Trade-offs
- **(+) Enhanced Clarity and Guidance:** Comprehensive documentation for FinOps, SecOps, and the new AI Release Agent provides users with detailed insights into system capabilities, deployment strategies, and operational best practices.
- **(+) Improved Performance Visibility:** Updated benchmarks in the main `README.md` clearly illustrate the system's high-throughput capabilities (25,300+ RPS with sub-7ms latency).
- **(+) Significant Cost Reduction:** The AWS FinOps simulation now demonstrates an improved cost reduction of 85% through optimized infrastructure choices (Graviton ARM64, Spot Instances, in-cluster datastores) and refined architectural strategies.
- **(+) Robust Policy Enforcement:** The introduction of Policy-as-Code documentation outlines a framework for automated security, FinOps, and architectural compliance using OPA/Rego, ensuring consistency and preventing misconfigurations.
- **(+) Automated Release Management:** The new AI Release Agent automates Semantic Versioning and release note generation, reducing manual effort and ensuring consistent, high-quality release documentation.
- **(-) Infrastructure Requirements:** The advanced FinOps and Policy-as-Code features rely on specific infrastructure configurations (e.g., EKS, Terraform, OPA/Conftest) and may require additional setup for users to fully leverage.
- **(-) AI Dependency:** The AI Release Agent requires access to the Gemini API, which may incur costs and necessitates API key management.

---

### v1.21.3

#### Changed Files & Core Modifications
- **Tooling & Automation:** The `Taskfile.yml` has been refactored to streamline task definitions, particularly for code quality and security checks. Pre-commit hooks in `.pre-commit-config.yaml` have been updated to exclude Helm chart directories from certain checks and to integrate a new security scanning tool, Checkov.

#### Reason for Changes
- **Enhanced Developer Experience & Security Posture:** This release focuses on improving the development workflow and strengthening the security of the codebase. By consolidating and refining tooling, we aim to reduce friction for developers and proactively identify potential security vulnerabilities earlier in the development cycle. The exclusion of Helm directories from specific checks prevents unnecessary noise and ensures focused scanning on relevant code.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Code Quality Enforcement:** Streamlined tasks and updated pre-commit hooks ensure more consistent application of code quality standards.
    - **Proactive Security Scanning:** Integration of Checkov enhances the detection of infrastructure and security misconfigurations.
    - **Reduced CI/CD Noise:** Excluding Helm directories from certain checks optimizes the scanning process.
    - **Developer Efficiency:** A more organized and efficient tooling setup leads to a better developer experience.
- **(-) Disadvantages / Notes:**
    - The addition of Checkov introduces a new dependency for infrastructure security scanning.

---

### v1.21.2

#### Changed Files & Core Modifications
- The Rego policy files (`policy/k8s_rules.rego`) have been updated. The syntax for defining denial rules has been adjusted from `deny contains msg if { ... }` to `deny[msg] { ... }`.

#### Reason for Changes
- This change was made to ensure compatibility with the latest version of `conftest`, a tool used for policy enforcement. The updated syntax aligns with the expected format for defining policy rules in the current `conftest` environment.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - Improved compatibility with the `conftest` tool, ensuring that policy checks continue to function as expected.
    - Maintains the integrity and effectiveness of existing Kubernetes security policies.
- **(-) Disadvantages / Notes:**
    - No functional changes to the policy logic itself. This is a syntax update for tooling compatibility.

---

### v1.21.1

#### Changed Files & Core Modifications
- The `.github/workflows/security.yaml` file has been updated to integrate new security scanning tools into the DevSecOps pipeline.
- A new `infra` filter has been added to the `detect-changes` job to specifically track changes within the `infrastructure/**` and `policy/**` directories.
- Two new jobs, `scan-terraform-checkov` and `scan-helm-conftest`, have been introduced.
    - `scan-terraform-checkov` leverages the Checkov tool to perform security audits on Terraform configurations.
    - `scan-helm-conftest` utilizes Conftest with OPA policies to audit Kubernetes configurations managed by Helm.

#### Reason for Changes
To enhance the security posture of our infrastructure and Kubernetes deployments, we have integrated automated security scanning tools directly into our CI/CD pipeline. This proactive approach aims to identify and mitigate security vulnerabilities and policy violations early in the development lifecycle.

#### Advantages & Architectural Trade-offs
- **(+) Advantages:**
    - **Improved Security:** Early detection of security misconfigurations in Terraform and Kubernetes manifests.
    - **Policy Enforcement:** Ensures adherence to defined security and compliance policies for infrastructure and Kubernetes resources.
    - **Automation:** Reduces manual effort and potential for human error in security reviews.
    - **DevSecOps Integration:** Seamlessly embeds security checks within the existing development workflow.
- **(-) Disadvantages / Notes:**
    - **Infrastructure Dependency:** Requires the GitHub Actions runner environment to have the necessary tools (Checkov, Helm, Conftest) installed or available.
    - **Policy Maintenance:** The effectiveness of the `scan-helm-conftest` job relies on the quality and maintenance of the OPA policies located in the `policy/` directory.

---

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
