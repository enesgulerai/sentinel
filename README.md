<div align="left">

# Sentinel: Real-Time AI Fraud Detection

*Enterprise-grade, event-driven anomaly detection pipeline with sub-millisecond ONNX inference.*

[![Go Version](https://img.shields.io/badge/Go-1.22+-00ADD8?style=flat-square)](https://go.dev)
[![Python Version](https://img.shields.io/badge/Python-3.11.9-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Rust Version](https://img.shields.io/badge/Rust-1.95.0-000000?style=flat-square&logo=rust&logoColor=white)](https://www.rust-lang.org)
[![Latest Release](https://img.shields.io/github/v/release/enesgulerdev/sentinel?style=flat-square&color=brgihgreen)](https://github.com/enesgulerdev/sentinel/releases)
[![License](https://img.shields.io/github/license/enesgulerdev/sentinel?style=flat-square)](LICENSE)

</div>

---
**Sentinel** is an enterprise-grade, real-time fraud detection system. It simulates high-throughput financial transactions via streaming (Redpanda/Kafka) and evaluates them in milliseconds using an optimized ONNX inference engine.

## Quick Start

### 1. Clone the Repository
Clone the project to your local machine and navigate into the root directory:

```bash
    git clone https://github.com/enesgulerdev/sentinel.git
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
    task env:install
```

### 4. Execute the ML Pipeline
Run the complete machine learning pipeline. This automated task will fetch the raw dataset using your provided `.env` variable, apply preprocessing transformations, and train the baseline model.

```bash
    task ml:pipeline
```

### 5. Launch and Manage Application
The Sentinel project utilizes a microservices architecture. Start the Docker containers to spin up the API gateway, and all other core services in detached mode:

```bash
    # Start all services
    task docker:on

    # Stop and remove containers, networks, and volumes
    task docker:off
```

## Local Services & Ports
Once the Docker containers are up and running, you can access the core services via the following local addresses:

| Service | Local URL |
| :--- | :--- |
| **Dashboard:** | http://localhost:8000/api/v1/dashboard |
| **API Gateway** | http://localhost:8000 |
| **Redpanda** | http://localhost:8080 |

## Troubleshooting

### `task: command not found`
Sentinel leverages the Taskfile runner for all automation. If the command is not recognized, install it:
* **macOS (Homebrew):** `brew install go-task`
* **Windows (Chocolatey/Scoop):** `choco install go-task` or `scoop install task`
* **Linux:** `sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d`

## Repository Structure & Deep Dives

Sentinel is built with a strictly modular architecture. While this guide covers local Docker deployment, you can explore the advanced components in their respective directories:

* **[Infrastructure & Kubernetes](infrastructure/k8s/README.md)**: Enterprise deployment manifests, service configurations, and orchestration details for scaling Sentinel in the cloud.
* **[Testing Suite](tests/README.md)**: Comprehensive unit tests, integration tests, and mock fixtures ensuring system reliability.
* **[Helm Deployment](infrastructure/helm/README.md)**: Unified and autonomous Helm charts for seamless local provisioning, encapsulating all stateful dependencies and isolated ML workloads.
