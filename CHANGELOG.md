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

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
