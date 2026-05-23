<div align="left">

# Sentinel: Real-Time AI Fraud Detection

*Enterprise-grade, event-driven anomaly detection pipeline with sub-millisecond ONNX inference.*

[![Go Version](https://img.shields.io/badge/Go-1.22+-00ADD8?style=flat-square)](https://go.dev)
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
    task docker:up

    # Stop and remove containers, networks, and volumes
    task docker:off
```

## Kubernetes Orchestration & Workload Isolation (Local Development via Kind)
*Note: If you experience any issues during the Kubernetes deployment, please refer to the Troubleshooting section at the bottom of this page.*

Sentinel provides streamlined `Taskfile` commands for local Kubernetes orchestration. The automated setup provisions a multi-node cluster and configures strict workload isolation (Taints, Tolerations, and Node Affinity) to eliminate resource contention between the heavy AI inference engine and stateful data stores.

### 1. Provision & Deploy the Architecture
Run the start command to execute the entire infrastructure setup automatically. This single command creates the multi-node Kind cluster, applies hardware isolation rules, builds the Docker images, loads them into the cluster, and deploys all application and infrastructure manifests sequentially.
```bash
    task k8s:start
```

### 2. Check Pod Status (Crucial)
Before accessing the services, ensure all pods have reached the `Running` state. If you attempt to port-forward while pods are in `Init` or `ContainerCreating` states, the connection will fail.
```bash
    task k8s:status
```

### 3. Access the Services
Run the following command to bind all necessary K8s ports (API Gateway and Redpanda Console) to your local machine simultaneously. This process runs in the foreground; simply press `Ctrl+C` to terminate all connections when done.
```bash
    task k8s:forward
```

### 4. Teardown & Clean
Once you are finished, clean up the entire Sentinel stack and completely destroy the local Kind cluster and its associated data to free up system resources.
```bash
    task k8s:off
```

### Optional: Architecture Stress Testing (HPA in Action)

Sentinel is designed with high availability and elasticity in mind. We use Kubernetes Horizontal Pod Autoscaling (HPA) to dynamically scale the stateless API layer based on sudden traffic spikes.

You can safely benchmark the API's scaling capabilities locally using [oha](https://github.com/hatoo/oha):

1. **Keep the Port-Forward Running:** Ensure `task k8s:forward` is running in your first terminal.
2. **Monitor the Autoscaler:** Open a second terminal and watch the HPA react in real-time:
   ```bash
   kubectl get hpa sentinel-api-hpa -w
   ```
3. Trigger the Load Test: Open a third terminal and blast the API with 250 concurrent workers for 60 seconds:
    ```bash
    task test:load-health
    ```
    *Observe the second terminal: You will see the CPU utilization spike dramatically, prompting Kubernetes to autonomously clone the API pods (up to 5 replicas) to distribute the load, maintaining a 100% success rate without dropping connections.*

## Local Services & Ports

Once the Docker containers are up and running, you can access the core services via the following local addresses:

| Service | Local URL |
| :--- | :--- |
| **API Gateway** | http://localhost:8000 |
| **Redpanda** | http://localhost:8080 |


## Testing & Performance

This project uses `pytest` for unit and integration testing, and `oha` for HTTP load testing. We use `Taskfile` to automate these processes.

### Running Unit and Integration Tests
To execute the entire test suite, which includes logic validation and idempotency checks, run the following command:

> **Prerequisite:** Before running any tasks, ensure your virtual environment is active to access project dependencies:

*   **Windows:** `.venv\Scripts\activate`
*   **macOS/Linux:** `source .venv/bin/activate`

```bash
    task test:run
```

### Running Performance Tests
To benchmark the API Gateway's connection capacity and measure the health endpoint's throughput under heavy concurrent load (250 workers for 1 minute), execute:

> **Prerequisite:** Ensure that Docker is running and your infrastructure (Redis, Redpanda) is healthy before starting load tests.

 ```bash
    task test:load-health
 ```
 *Note: Note on Performance Bottlenecks:
If you observe high average latency (ms) during this extreme load test, it is because the API is currently deployed as a single, standalone Docker container. This creates a natural bottleneck at the single-process level. In the upcoming Kubernetes (K8s) deployment phase, we will implement horizontal scaling. By increasing the pod replica count behind a load balancer, the concurrent traffic will be distributed across multiple instances, effectively mitigating this latency issue and maximizing overall throughput.*

### End-to-End Verification (Sanity Check)

To ensure the data pipeline is successfully capturing events, running AI inference, and persisting results, you can trigger a mock transaction and query the database directly.

**1. Forward the API Port**
Keep this running in a separate terminal:
```bash
    task k8s:forward
```

**2. Trigger a Test Transaction**
Send a mock JSON payload to the Go API Gateway:

**For Linux, macOS, or Git Bash:**
```bash
    curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "TEST-1001", "user_id": "usr_777", "Amount": 999.99, "Time": 10.0, "V1": 0.0, "V2": 0.0, "V3": 0.0}'
```
**For Windows PowerShell:**
```powershell
    Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transactions" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"transaction_id": "TEST-1001", "user_id": "usr_777", "Amount": 999.99, "Time": 10.0, "V1": 0.0, "V2": 0.0, "V3": 0.0}'
```
*(Note: The full AI model requires all V1-V28 features, omitted here for brevity.)*

**3. Verify Persistence & AI Risk Score**
Query the PostgreSQL statefulset directly to see the AI-assigned risk score:
```bash
    kubectl exec -it postgres-0 -- psql -U sentinel -d sentinel_db -c "SELECT transaction_id, risk_score, created_at FROM transactions LIMIT 5;"
```

*Expected Output: A table displaying the transaction and its newly calculated risk score, proving the End-to-End event-driven flow is fully operational.*

## Troubleshooting

### `task: command not found`
Sentinel leverages the Taskfile runner for all automation. If the command is not recognized, install it:
* **macOS (Homebrew):** `brew install go-task`
* **Windows (Chocolatey/Scoop):** `choco install go-task` or `scoop install task`
* **Linux:** `sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d`

### `oha: command not found`
The local load-testing tasks strictly depend on the `oha` HTTP load generator:
* **macOS (Homebrew):** `brew install oha`
* **Windows (Winget):** `winget install hatoo.oha`
* **Linux (Arch):** `pacman -S oha`
* **Universal (Cargo):** `cargo install oha`

### `kind: command not found`
If the Kubernetes provisioning fails due to a missing Kind CLI, install it and restart your terminal:
* **macOS (Homebrew):** `brew install kind`
* **Windows (Winget):** `winget install Kubernetes.kind`
* **Linux:** `curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64 && chmod +x ./kind && sudo mv ./kind /usr/local/bin/kind`

*(Note: Do not run `kind create cluster` manually. Always use `task k8s:start` to ensure the custom multi-node infrastructure and workload isolation rules are applied correctly.)*
