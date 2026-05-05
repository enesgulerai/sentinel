<div align="left">

# Sentinel: Real-Time AI Fraud Detection

*Enterprise-grade, event-driven anomaly detection pipeline with sub-millisecond ONNX inference.*

![Python](https://img.shields.io/badge/python-000000?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=for-the-badge&logo=fastapi&logoColor=009688)
![Docker](https://img.shields.io/badge/docker-000000?style=for-the-badge&logo=docker&logoColor=2496ED)
<br>
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-000000?style=for-the-badge&logo=apachekafka&logoColor=white)
![Redis](https://img.shields.io/badge/redis-000000?style=for-the-badge&logo=redis&logoColor=FF4438)
![Prefect](https://img.shields.io/badge/Prefect-000000?style=for-the-badge&logo=prefect&logoColor=2670FF)
![Trivy](https://img.shields.io/badge/Trivy-000000?style=for-the-badge&logo=aquasecurity&logoColor=1904DA)
![Bandit](https://img.shields.io/badge/Bandit-000000?style=for-the-badge&logo=python&logoColor=ffdd54)
![Taskfile](https://img.shields.io/badge/Taskfile-000000?style=for-the-badge&logo=task&logoColor=29BEB0)

</div>

---
**Sentinel** is an enterprise-grade, real-time fraud detection system. It simulates high-throughput financial transactions via streaming (Redpanda/Kafka) and evaluates them in milliseconds using an optimized ONNX inference engine.

## Quick Start

### 1. Clone the Repository
Clone the project to your local machine and navigate into the root directory:

```bash
    git clone https://github.com/enesgulerai/sentinel.git
    cd sentinel
```

### 2. Configure Environment Variables
The data ingestion process requires a Google Drive File ID to fetch the raw dataset via gdown. Copy the example environment file to create your local configuration:

```bash
    cp .env.example .env
```

### 3. Install Dependencies
Install all required Python packages and set up the local development environment. This command utilizes `uv` to create a virtual environment and strictly syncs the dependencies locked in `uv.lock`.

```bash
    task install
```

### 4. Execute the ML Pipeline
Run the complete machine learning pipeline. This automated task will fetch the raw dataset using your provided `.env` variable, apply preprocessing transformations, and train the baseline model.

```bash
    task pipeline
```

### 5. Launch and Manage Application
The Sentinel project utilizes a microservices architecture. Start the Docker containers to spin up the Prefect orchestration server, API gateway, and all other core services in detached mode:

```bash
    # Start all services
    task up

    # Stop and remove containers, networks, and volumes
    task down
```

## Local Services & Ports

Once the Docker containers are up and running, you can access the core services via the following local addresses:

| Service | Local URL |
| :--- | :--- |
| **Prefect Dashboard** | http://localhost:4200 |
| **API Gateway** | http://localhost:8000 |
| **Redpanda Console** | http://localhost:8080 |
| **Streamlit UI** | http://localhost:8501 |

## Testing & Performance

This project uses `pytest` for unit and integration testing, and `oha` for HTTP load testing. We use `Taskfile` to automate these processes.

### Prerequisites

### Running Unit and Integration Tests
To execute the entire test suite, which includes logic validation and idempotency checks, run the following command:

```bash
    task test
```

### Running Performance Tests
To benchmark the API Gateway's connection capacity and measure the health endpoint's throughput under heavy concurrent load (250 workers for 1 minute), execute:

 ```bash
    task load-test-health
 ```
 * *Note: Note on Performance Bottlenecks:
If you observe high average latency (ms) during this extreme load test, it is because the API is currently deployed as a single, standalone Docker container. This creates a natural bottleneck at the single-process level. In the upcoming Kubernetes (K8s) deployment phase, we will implement horizontal scaling. By increasing the pod replica count behind a load balancer, the concurrent traffic will be distributed across multiple instances, effectively mitigating this latency issue and maximizing overall throughput.*


## Troubleshooting

### "task: command not found"
Sentinel leverages the **Taskfile** runner for efficient task automation and documentation. If the `task` command is not recognized, you need to install the task runner on your system:

*   **macOS (Homebrew):** `brew install go-task/tap/go-task`
*   **Windows (Chocolatey or Scoop):** `choco install go-task` or `scoop install task`
*   **Linux:** `sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d`

Alternatively, you can visit the [official Task installation guide](https://taskfile.dev/installation/) for more options.

### "oha: command not found"
**Issue:** Running `task load-test-health` fails with a "command not found: oha" error.

**Solution:** The performance testing tasks strictly depend on the `oha` HTTP load generator. You can quickly install it directly via your system's package manager:

*   **Windows (Winget):** `winget install hatoo.oha`
*   **macOS (Homebrew):** `brew install oha`
*   **Linux (Arch):** `pacman -S oha`
*   **Universal (Cargo/Rust):** `cargo install oha`

After installation, ensure that the installation directory is added to your system's PATH environment variable.
