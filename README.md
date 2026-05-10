<div align="left">

# Sentinel: Real-Time AI Fraud Detection

*Enterprise-grade, event-driven anomaly detection pipeline with sub-millisecond ONNX inference.*

![Python](https://img.shields.io/badge/python-000000?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=for-the-badge&logo=fastapi&logoColor=009688)
![Docker](https://img.shields.io/badge/docker-000000?style=for-the-badge&logo=docker&logoColor=2496ED)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-000000?style=for-the-badge&logo=apachekafka&logoColor=white)
![Redis](https://img.shields.io/badge/redis-000000?style=for-the-badge&logo=redis&logoColor=FF4438)
![Prefect](https://img.shields.io/badge/Prefect-000000?style=for-the-badge&logo=prefect&logoColor=2670FF)
![Trivy](https://img.shields.io/badge/Trivy-000000?style=for-the-badge&logo=aquasecurity&logoColor=1904DA)
![Bandit](https://img.shields.io/badge/Bandit-000000?style=for-the-badge&logo=python&logoColor=ffdd54)
![Taskfile](https://img.shields.io/badge/Taskfile-000000?style=for-the-badge&logo=task&logoColor=29BEB0)
![Kubernetes](https://img.shields.io/badge/Kubernetes-000000?style=for-the-badge&logo=kubernetes&logoColor=326CE5)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-000000?style=for-the-badge&logo=postgresql&logoColor=4169E1)

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

## Local Kubernetes Development (Kind)
*Note: If you experience any issues or hanging pods during the Kubernetes deployment, please refer to the Troubleshooting section at the bottom of this page.*

Sentinel provides streamlined Taskfile commands for local Kubernetes orchestration, eliminating the need for complex `kubectl` management.

1. **Build and Load Images:**
   Ensure your local Kind cluster has the latest images:
   ```bash
   task k8s:build-load
   ```

2. **Deploy the Architecture:**
    Apply all infrastructure and application manifests:
    ```bash
    task k8s:up
    ```

3. **Check Pod Status (Crucial):**
    Before accessing the services, ensure all pods have reached the `Running` state. If you attempt to port-forward while pods are in `Init` or `ContainerCreating` states, the connection will fail.
    ```bash
    task k8s:status
    ```

4. **Access the Services:**
    Run the following command to bind all necessary K8s ports to your local machine simultaneously. This process runs in the foreground; simply press `Ctrl+C` to terminate all connections when done.
    ```bash
    task k8s:forward
    ```

5. **Teardown:**
    ```bash
    task k8s:down
    ```

### Optional: Architecture Stress Testing (HPA in Action)

Sentinel is designed with high availability and elasticity in mind. We use Kubernetes Horizontal Pod Autoscaling (HPA) to dynamically scale the stateless API and UI layers based on traffic spikes.

You can safely benchmark the API's scaling capabilities locally using [oha](https://github.com/hatoo/oha):

1. **Keep the Port-Forward Running:** Ensure `task k8s:forward` is running in your first terminal.
2. **Monitor the Autoscaler:** Open a second terminal and watch the HPA react in real-time:
   ```bash
   kubectl get hpa -w
   ```
3. **Trigger the Load Test:** Open a third terminal and blast the API with 200 concurrent workers for 60 seconds:
    ```bash
    oha -z 60s -c 200 http://localhost:8000/docs
    ```

    *Observe the second terminal: You will see the CPU utilization spike, prompting Kubernetes to autonomously clone the API pods (up to 5 replicas) to distribute the load, maintaining a 100% success rate without dropping connections.*

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

### Running Unit and Integration Tests
To execute the entire test suite, which includes logic validation and idempotency checks, run the following command:

> **Prerequisite:** Before running any tasks, ensure your virtual environment is active to access project dependencies:

*   **Windows:** `.venv\Scripts\activate`
*   **macOS/Linux:** `source .venv/bin/activate`

```bash
    task test
```

### Running Performance Tests
To benchmark the API Gateway's connection capacity and measure the health endpoint's throughput under heavy concurrent load (250 workers for 1 minute), execute:

> **Prerequisite:** Ensure that Docker is running and your infrastructure (Redis, Redpanda) is healthy before starting load tests.

 ```bash
    task load-test-health
 ```
 * *Note: Note on Performance Bottlenecks:
If you observe high average latency (ms) during this extreme load test, it is because the API is currently deployed as a single, standalone Docker container. This creates a natural bottleneck at the single-process level. In the upcoming Kubernetes (K8s) deployment phase, we will implement horizontal scaling. By increasing the pod replica count behind a load balancer, the concurrent traffic will be distributed across multiple instances, effectively mitigating this latency issue and maximizing overall throughput.*

### Database Verification (Sanity Check)

To ensure the end-to-end data pipeline is successfully capturing events and persisting them to PostgreSQL, you can query the database directly from within the Kubernetes cluster.

Run the following command to check the latest records and their AI-assigned risk scores:

1. Prerequisite: Port Forwarding
Since the API is running inside the cluster, you must first forward the port to your local machine:

```bash
    task k8s:forward
```
*Note: Keep this terminal open or run it in the background.*


2. Trigger a Test Transaction
Send a mock transaction with all required features to the API:

```bash
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/transactions" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"transaction_id": "TEST-1001", "user_id": "user_777", "Amount": 999.99, "Time": 10.0, "V1": 0.0, "V2": 0.0, "V3": 0.0, "V4": 0.0, "V5": 0.0, "V6": 0.0, "V7": 0.0, "V8": 0.0, "V9": 0.0, "V10": 0.0, "V11": 0.0, "V12": 0.0, "V13": 0.0, "V14": 0.0, "V15": 0.0, "V16": 0.0, "V17": 0.0, "V18": 0.0, "V19": 0.0, "V20": 0.0, "V21": 0.0, "V22": 0.0, "V23": 0.0, "V24": 0.0, "V25": 0.0, "V26": 0.0, "V27": 0.0, "V28": 0.0}'
```

3. Verify Inference Logs
Check if the Consumer captured the event from Redpanda and processed it via the ONNX model:

```bash
kubectl logs deploy/sentinel-consumer
```

4. Query the Database
Directly query the PostgreSQL statefulset to see the persisted record and its AI-assigned risk score:

```bash
    kubectl exec -it postgres-0 -- psql -U sentinel -d sentinel_db -c "SELECT transaction_id, user_id, amount, risk_score FROM transactions LIMIT 10;"
```

*Expected Output: If the pipeline is functioning correctly, you should see a table displaying the transactions that have passed through Redpanda and the AI Consumer.*


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

### "Missing kind command on Windows"
If you encounter a `"kind": executable file not found in $PATH` error during the build phase, it means the Kind CLI is not installed on your system.
1. Open PowerShell as Administrator and install Kind via winget:
    ```bash
    winget install Kubernetes.kind
    ```

2. Restart your terminal (VS Code or PowerShell) to refresh the environment variables.

3. Create your local Kind cluster before running the tasks:
    ```bash
    kind create cluster
    ```

### HPA Targets Showing `<unknown>` (Missing Metrics Server):
By default, local Kubernetes distributions like Kind do not include the `metrics-server`, which is strictly required for the Horizontal Pod Autoscaler (HPA) to monitor CPU/Memory usage. If your HPA cannot read metrics, install and patch the server:

1. Apply the official metrics-server manifest:
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

2. Patch the deployment to allow insecure TLS (a requirement for local Kind nodes without proper certificates):
    ```bash
    kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
    ```
