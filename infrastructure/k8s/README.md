# Kubernetes Orchestration & Workload Isolation (Local Development via Kind)
*Note: If you experience any issues during the Kubernetes deployment, please refer to the Troubleshooting section at the bottom of this page.*

Sentinel provides streamlined `Taskfile` commands for local Kubernetes orchestration. The automated setup provisions a multi-node cluster and configures strict workload isolation (Taints, Tolerations, and Node Affinity) to eliminate resource contention between the heavy AI inference engine and stateful data stores.

## Advanced Kubernetes Scheduling: Solving the "Noisy Neighbor" Problem

In our pursuit of highly optimized performance and sub-millisecond tail latencies, we encountered the classic "Noisy Neighbor" problem within our initial Single-Node setup. Running our lightweight, high-throughput Go API alongside I/O-intensive datastores (Postgres/Redpanda/Redis) and a CPU-hungry XGBoost AI inference engine (Consumer) created severe resource contention. Whenever the AI model spiked to 100% CPU utilization, the Go API and Redis suffered from instantaneous latency spikes.

To achieve strict resource isolation, we evolved the architecture to a **Multi-Node Cluster** (1 Control Plane, 2 Workers) and implemented advanced Kubernetes scheduling strategies:

### 1. Storage Isolation via Node Affinity
* **Strategy:** We labeled one of our worker nodes strictly for stateful workloads (`role=storage`).
* **Implementation:** We applied **Node Affinity** rules to the Postgres, Redis, and Redpanda manifests.
* **Result:** Kubernetes is now forced to schedule these stateful components exclusively on the storage node. Disk I/O operations are highly centralized, guaranteeing they never bottleneck the API or AI compute layers.

### 2. AI Inference Quarantine via Taints & Tolerations
* **Strategy:** We tainted our second worker node (`dedicated=ai-inference:NoSchedule`), essentially hanging a "Do Not Enter" sign for standard workloads.
* **Implementation:** We equipped our heavy Python Consumer manifest with the exact **Tolerations** required to bypass this taint.
* **Result:** The XGBoost inference model now operates in absolute quarantine. No other pods (such as the Go API or databases) can be scheduled on this node. The AI engine can freely consume 100% of its node's CPU without causing a single millisecond of latency degradation to the rest of the ecosystem.

## Quick Start

### 1. Provision & Deploy the Architecture
Run the start command to execute the entire infrastructure setup automatically. This single command creates the multi-node Kind cluster, applies hardware isolation rules, builds the Docker images, loads them into the cluster, and deploys all application and infrastructure manifests sequentially.
```bash
    task k8s:on
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

**Local Port Mappings**

When running `task k8s:forward`, the following ports will be bound to your local machine (`localhost`). Please ensure these ports are available and not actively held by other background processes before initiating the connection.

| Service | Local Port | Protocol | Description |
| :--- | :--- | :--- | :--- |
| **Go API Gateway** | `8000` | HTTP | Main entry point for the REST API (Event Ingestion). |
| **Redpanda Console**| `8080` | HTTP | Web UI for monitoring Kafka topics, brokers, and messages. |

*(Note: Internal communication between microservices, such as PostgreSQL on 5432 or Redis on 6379, happens entirely within the isolated Kubernetes cluster network and does not require local port binding.)*

### Optional: 4. End-to-End Verification (Sanity Check)
To ensure the data pipeline is successfully capturing events, running AI inference, and persisting results, you can trigger a mock transaction and query the database directly.

**1. Trigger a Test Transaction**
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

**2. Verify Persistence & AI Risk Score**
Query the PostgreSQL statefulset directly to see the AI-assigned risk score:
```bash
    kubectl exec -it postgres-0 -- psql -U sentinel -d sentinel_db -c "SELECT transaction_id, risk_score, created_at FROM transactions LIMIT 5;"
```
*Expected Output: A table displaying the transaction and its newly calculated risk score, proving the End-to-End event-driven flow is fully operational.*

### 5. Teardown & Clean
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

## Troubleshooting

### `kind: command not found`
If the Kubernetes provisioning fails due to a missing Kind CLI, install it and restart your terminal:
* **macOS (Homebrew):** `brew install kind`
* **Windows (Winget):** `winget install Kubernetes.kind`
* **Linux:** `curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64 && chmod +x ./kind && sudo mv ./kind /usr/local/bin/kind`

*(Note: Do not run `kind create cluster` manually. Always use `task k8s:on` to ensure the custom multi-node infrastructure and workload isolation rules are applied correctly.)*
