# Testing & Performance

This project uses `pytest` for unit and integration testing, and `oha` for HTTP load testing. We use `Taskfile` to automate these processes.

## Running Unit and Integration Tests
To execute the entire test suite, which includes logic validation and idempotency checks, run the following command:

> **Prerequisite:** Before running any tasks, ensure your virtual environment is active to access project dependencies:

*   **Windows:** `.venv\Scripts\activate`
*   **macOS/Linux:** `source .venv/bin/activate`

```bash
    task test:run
```

## Running Performance Tests
To benchmark the API Gateway's connection capacity and measure the health endpoint's throughput under heavy concurrent load (250 workers for 1 minute), execute:

> **Prerequisite:** Ensure that Docker is running and your infrastructure (Redis, Redpanda) is healthy before starting load tests.

 ```bash
    task test:load-health
 ```
 *Note on Performance Bottlenecks:
If you observe high average latency (ms) during this extreme load test, it is because the API is currently deployed as a single, standalone Docker container. This creates a natural bottleneck at the single-process level. In the upcoming Kubernetes (K8s) deployment phase, we will implement horizontal scaling. By increasing the pod replica count behind a load balancer, the concurrent traffic will be distributed across multiple instances, effectively mitigating this latency issue and maximizing overall throughput.*

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
