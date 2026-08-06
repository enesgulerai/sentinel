<div align="left">

# Sentinel: Enterprise Real-Time Fraud & Anomaly Ingestion Engine
### Module: Testing Architecture

</div>

---

## Overview
This module houses the deterministic, polyglot testing suite for the Sentinel platform. It guarantees the reliability of the system across all microservices by executing unit, integration, and performance tests. To achieve isolated, millisecond execution, all external dependencies (such as Redis, Redpanda, and PostgreSQL) are strictly mocked in-memory utilizing dependency injection.

## Architecture & Workflow
The testing architecture spans across three different programming languages and includes dedicated load testing for system benchmarks. The execution lifecycle enforces a strict **halt-on-failure** policy; if any test in the sequence fails, the pipeline immediately stops to prevent faulty code progression.

### Testing Stack

| Environment | Frameworks & Tooling | Focus Area |
| :--- | :--- | :--- |
| **Go (API Gateway)** | `testing`, `httptest`, `redismock` | API routing, state management, HTTP handlers. |
| **Rust (Validator)** | `cargo test` | Strict schema validation, fast serialization. |
| **Python (Consumer)**| `pytest`, `pytest-asyncio`, `AsyncMock` | Async event pipelines, inference engine mocking. |
| **Load Testing** | `k6` | High-concurrency HTTP stress generation. |

## Prerequisites
Ensure the respective language environments and orchestration tools are available on your system before executing the tests:
*   **[Taskfile](https://taskfile.dev/installation/):** Orchestrator (`brew install go-task` / `choco install go-task`)
*   **Go Toolchain:** Required for API tests
*   **Rust & Cargo:** Required for Validator tests
*   **Python (uv):** Required for Consumer/Inference tests
*   **k6:** Required for running the load testing fixtures

## Quick Start & Usage
The master orchestration command runs all language test suites sequentially.

```bash
# 1. Activate Python virtual environment (Required for ML tests)
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 2. Execute universal test orchestration
task test:all
```

## Configuration & Environment
Because the test suite relies on strict dependency injection and in-memory mocking, it does not require live instances of Redpanda, Redis, or PostgreSQL. Environment variables required during the test runs are securely injected and managed at runtime via the `Taskfile` and the respective testing frameworks.
