# Sentinel Test Architecture

This project utilizes a high-performance polyglot monorepo architecture. Our testing suite reflects this by using native testing frameworks for each language ecosystem, fully orchestrated via `Taskfile`. 

External infrastructure dependencies (Redis, Redpanda, PostgreSQL) are mocked in-memory using dependency injection. This ensures all unit and integration tests run in milliseconds, completely isolated and deterministic.

## Testing Stack
* **Go (API Gateway):** Native `testing` package, `httptest`, and `redismock`.
* **Rust (Validator):** Native `cargo test` for strict schema and serialization validation.
* **Python (ML Consumer):** `pytest` with `pytest-asyncio` and `AsyncMock` for complex data pipelines.
* **Load Testing:** `oha` (Rust-based, ultra-fast HTTP load generator).

## Prerequisites
Before running the tests, ensure you have the Go and Rust toolchains installed. For the Python ML Consumer tests, you must activate your virtual environment:

* **Windows:** `.venv\Scripts\activate`
* **macOS/Linux:** `source .venv/bin/activate`

---

## Running the Tests

### 1. Execute the Entire Polyglot Suite
To run the Go, Rust, and Python test suites sequentially, use the master orchestration command:
```bash
    task test:all
```
*Note: This task enforces a strict pipeline. If any language's test suite fails, the chain will halt immediately to prevent faulty code from proceeding.*

## Running Performance Tests
To benchmark the API Gateway's connection capacity and measure the health endpoint's throughput under heavy concurrent load (250 workers for 1 minute), execute:

> **Prerequisite:** Ensure that Docker is running and your infrastructure (Redis, Redpanda) is healthy before starting load tests.

 ```bash
    task test:load-health
 ```

*Note on Performance Bottlenecks: If you observe high average latency (ms) during this extreme load test, it is because the API is currently deployed as a single, standalone Docker container. This creates a natural bottleneck at the single-process level. In the upcoming Kubernetes (K8s) deployment phase, we will implement horizontal scaling. By increasing the pod replica count behind a load balancer, the concurrent traffic will be distributed across multiple instances, effectively mitigating this latency issue and maximizing overall throughput.*

## Live Telemetry Simulation (UI Test)

To observe the real-time AI fraud detection stream in action, you can generate live mock traffic that flows through the ingestion pipeline (Redpanda/Kafka) and reflects directly on the Web UI.

**1. Open the Dashboard**
Ensure your infrastructure is running (`task docker:on`), then navigate to the telemetry dashboard in your browser:
http://localhost:8000/api/v1/dashboard

**2. Generate Live Traffic**
Open a new terminal window in the project root and start the automated traffic generator:

```bash
task test:traffic
```

## Troubleshooting

### `oha: command not found`
The local load-testing tasks strictly depend on the `oha` HTTP load generator:
* **macOS (Homebrew):** `brew install oha`
* **Windows (Winget):** `winget install hatoo.oha`
* **Linux (Arch):** `pacman -S oha`
* **Universal (Cargo):** `cargo install oha`
