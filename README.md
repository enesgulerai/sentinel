<div align="left">

# Sentinel: Real-Time AI Fraud Detection

*Enterprise-grade, event-driven anomaly detection pipeline with sub-millisecond ONNX inference.*

[![Go Version](https://img.shields.io/badge/Go-1.26+-00ADD8?style=flat-square)](https://go.dev)
[![Python Version](https://img.shields.io/badge/Python-3.11.9-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Rust Version](https://img.shields.io/badge/Rust-1.95.0-000000?style=flat-square&logo=rust&logoColor=white)](https://www.rust-lang.org)
[![Latest Release](https://img.shields.io/github/v/release/enesgulerdev/sentinel?style=flat-square&color=brgihgreen)](https://github.com/enesgulerdev/sentinel/releases)
[![License](https://img.shields.io/github/license/enesgulerdev/sentinel?style=flat-square)](LICENSE)

</div>

---

**Sentinel** is an enterprise-grade, real-time fraud detection system. It simulates high-throughput financial transactions via streaming (Redpanda/Kafka) and evaluates them in milliseconds using an optimized ONNX inference engine.

## Quick Start

### Prerequisites
- [Task](https://taskfile.dev/installation/) (`brew install go-task` / `choco install go-task`)
- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv)

### Setup & Run

```bash
# 1. Clone repository
git clone https://github.com/enesgulerdev/sentinel.git
cd sentinel

# 2. Configure environment (Requires Google Drive File ID for gdown)
cp .env.example .env

# 3. Install dependencies via uv
task env:install

# 4. Execute ML Pipeline (Fetch dataset, preprocess, train baseline)
task ml:pipeline

# 5. Start microservices (API Gateway, Redpanda, etc.)
task docker:on
```

### Container Management
```bash
task docker:on    # Start all services
task docker:down  # Stop gracefully (keeps images intact)
task docker:off   # Full wipe (removes containers, networks, volumes, images)
```

## Local Services

| Service | Local URL |
| :--- | :--- |
| **API Gateway** | `http://localhost:8000` |
| **Redpanda** | `http://localhost:8080` |


## Architecture & Deep Dives

Explore the sub-modules for advanced deployment, scaling, and observability patterns:

| Module / Component | Description |
| :--- | :--- |
| **[Testing Suite](tests/README.md)** | Unit, integration, and mock fixtures. |
| **[Helm Workloads](infrastructure/helm/README.md)** | Autonomous local provisioning for stateful dependencies and isolated ML workloads. |
| **[GitOps & CD](infrastructure/argocd/README.md)** | Zero-touch deployment architecture using ArgoCD and Jenkins for deterministic state synchronization. |
| **[AWS FinOps Simulation](infrastructure/terraform/aws-finops-mock/README.md)** | Infracost model demonstrating system scale to **25,300+ RPS** with a **73% cost reduction** under enterprise conditions. |
