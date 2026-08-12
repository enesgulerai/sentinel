<div align="left">

# Sentinel: Enterprise Real-Time Fraud & Anomaly Ingestion Engine

*Enterprise-grade, event-driven anomaly detection pipeline with sub-millisecond ONNX inference.*

[![Go Version](https://img.shields.io/badge/Go-1.26+-00ADD8?style=flat-square)](https://go.dev)
[![Python Version](https://img.shields.io/badge/Python-3.11.9-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org)
[![Rust Version](https://img.shields.io/badge/Rust-1.95.0-000000?style=flat-square&logo=rust&logoColor=white)](https://www.rust-lang.org)
[![Latest Release](https://img.shields.io/github/v/release/enesgulerdev/sentinel?style=flat-square&color=brgihgreen)](https://github.com/enesgulerdev/sentinel/releases)
[![License](https://img.shields.io/github/license/enesgulerdev/sentinel?style=flat-square)](LICENSE)

</div>

---

## Overview
**Sentinel** is an enterprise-grade, real-time fraud detection platform designed to handle high-throughput financial transaction streams with sub-millisecond AI inference latency.

The system simulates live financial transactions through an event-driven streaming pipeline powered by Redpanda (Kafka-compatible), validates payloads at high speed via a Rust stream processor, and evaluates fraud risks using an optimized Python ONNX runtime environment.

## Architecture & Workflow

### Performance Benchmark
![Performance Benchmark](docs/images/rps-report/k6-load-test.png)
*Peak Performance Benchmark: Sustaining 25,300+ RPS with 7.79ms average latency over 4.5 million requests.*

> **Note:** Peak 25,300+ RPS was achieved under optimal hardware conditions. Standard local Docker Desktop deployments typically yield ~18,000+ RPS due to local CPU and network bridge constraints.

### System Data Flow

```mermaid
graph TD
    %% Styling
    classDef go fill:#00ADD8,stroke:#fff,stroke-width:2px,color:#fff;
    classDef rust fill:#DEA584,stroke:#fff,stroke-width:2px,color:#000;
    classDef python fill:#FFD43B,stroke:#306998,stroke-width:2px,color:#306998;
    classDef infra fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef storage fill:#ff9900,stroke:#fff,stroke-width:2px,color:#fff;
    classDef broker fill:#8B0000,stroke:#fff,stroke-width:2px,color:#fff;

    %% Nodes
    Client([Client / K6 Load Tester])

    subgraph API Layer
        Gateway[Go Gin Gateway]:::go
    end

    subgraph Streaming & Validation
        Redis[(Redis / Valkey<br>Idempotency)]:::infra
        Broker1{Redpanda<br>raw-events}:::broker
        Validator[Rust Stream Processor]:::rust
        Broker2{Redpanda<br>clean-events}:::broker
    end

    subgraph AI & Persistence
        Consumer[Python Inference Engine<br>ONNX Model]:::python
        S3[(AWS S3 / LocalStack<br>Audit Logs)]:::storage
        DB[(PostgreSQL)]:::infra
    end

    %% Edges (Flow)
    Client -->|HTTP POST| Gateway
    Gateway -->|1. Check tx_hash| Redis
    Redis -.->|Duplicate? Block| Gateway
    Gateway -->|2. Fire & Forget| S3
    Gateway -->|3. Publish| Broker1
    Broker1 -->|4. Consume Batch| Validator
    Validator -->|5. Type Check & Validate| Validator
    Validator -->|6. Publish Validated| Broker2
    Broker2 -->|7. Consume Batch| Consumer
    Consumer -->|8. Fraud Inference| Consumer
    Consumer -->|9. Persist Result| DB
```

### Module Documentation
Explore the sub-modules for advanced deployment, scaling, policy enforcement, and observability patterns:

| Module / Component | Description |
| :--- | :--- |
| **[Testing Suite](tests/README.md)** | Unit, integration, and mock fixtures. |
| **[Helm Workloads](infrastructure/helm/README.md)** | Autonomous local provisioning for stateful dependencies and isolated ML workloads. |
| **[GitOps & CD](infrastructure/argocd/README.md)** | Zero-touch deployment architecture using ArgoCD and automated CI/CD pipelines. |
| **[AWS FinOps Simulation](infrastructure/terraform/aws-finops-mock/README.md)** | Infracost model demonstrating system scale to **25,300+ RPS** with an **85% cost reduction** under enterprise conditions. |
| **[Policy & Governance](policy/README.md)** | Enterprise Policy-as-Code standards enforcing infrastructure, container, and Kubernetes security via OPA/Rego. |
| **[AI Release Agent](agent/release/README.md)** | Autonomous, AI-driven Python agent for dynamic Semantic Versioning and automated release notes generation via Gemini. |
| **[AI Doc Agent](agent/doc/README.md)** | Autonomous, AI-driven Engineering Council that analyzes git diffs to generate weekly persona-based architectural reviews. |
| **[Local AWS Simulation](infrastructure/terraform/localstack/README.md)** | Fully offline AWS S3 audit logging and event routing simulation via LocalStack. |

## Prerequisites
Ensure the following tools are installed before running the platform locally:
*   **[Taskfile](https://taskfile.dev/installation/):** Task runner (`brew install go-task` / `choco install go-task`)
*   **Docker & Docker Compose:** Required for containerized local runtime
*   **[uv](https://github.com/astral-sh/uv):** Ultra-fast Python package installer
*   **k6:** Required for executing performance load tests

## Quick Start & Usage

### 1. Setup Environment
```bash
# Clone repository
git clone https://github.com/enesgulerdev/sentinel.git
cd sentinel

# Configure environment variables
cp .env.example .env

# Install Python dependencies via uv
task env:setup
```

### 2. Execute ML Pipeline & Local Services
```bash
# Execute ML Pipeline (Fetch dataset, preprocess, train baseline model)
task ml:pipeline

# Start local microservices (API Gateway, Redpanda, Redis, etc.)
task docker:up
```

### 3. Verification & Load Testing
```bash
# Run k6 load tests to verify system throughput
k6 run tests/fixtures/loadtest.js
```

### 4. Container Management
```bash
task docker:up    # Start all services
task docker:down  # Stop services gracefully (retains container images)
task docker:nuke   # Full wipe (removes containers, networks, volumes, and images)
```

## Configuration & Environment

### Local Service Endpoints
When running locally, Sentinel exposes the following service interfaces:

| Service | Local URL / Endpoint | Protocol | Description |
| :--- | :--- | :--- | :--- |
| **API Gateway** | `http://localhost:8000` | HTTP | Ingestion gateway endpoint |
| **Redpanda Console** | `http://localhost:8080` | HTTP | Message broker UI & topic inspector |
