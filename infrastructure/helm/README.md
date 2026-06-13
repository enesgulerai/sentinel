# Sentinel Local Infrastructure

This directory contains the Infrastructure as Code (IaC) configuration designed to autonomously deploy all independent components of the Sentinel project (Postgres, Redis, Redpanda, Go API Gateway, Rust Validator, and Asynchronous Python ML Consumer) as a single, unified system.

## Advanced Architecture: Solving the "Noisy Neighbor" Problem
To achieve sub-millisecond tail latencies and strict resource isolation, we utilize advanced Kubernetes scheduling:
* **Storage Isolation (Node Affinity):** I/O-heavy datastores (Postgres, Redis, Redpanda) are forced onto dedicated storage nodes.
* **AI Inference Quarantine (Taints & Tolerations):** The CPU-hungry XGBoost AI inference engine operates in absolute quarantine. It can consume 100% of its dedicated node's CPU without causing latency degradation to the Go API.
* **Zero-Waste Auto-Scaling (HPA):** The stateless Go API Gateway is governed by a Horizontal Pod Autoscaler (HPA), dynamically cloning itself to absorb traffic spikes while maintaining strict, optimized memory limits (256Mi).

---

## Quick Start (Helm)

Follow these steps to bootstrap the entire system in your local Kubernetes environment.

### 1. Provision & Deploy
Run the following task to deploy the unified Helm chart into an isolated namespace. This replaces legacy raw K8s manifests with a Single Source of Truth.
```bash
task helm:on
```

### 2. Verify System Status
Watch all pods transition to the Running state. (Note: Redpanda and Postgres may take a minute to establish quorum and initialize).
```bash
task helm:status
```

### 3. Establish Connections (Crucial)
Before testing, you must bind the isolated K8s network to your local machine. Run this and leave the terminal open:
```bash
task helm:forward
```

### 4. Observability & Monitoring (Optional)
To visualize the real-time health, CPU/RAM usage, and ultra-low resource footprint of the microservices (e.g., the ~15MB Go API and ~3MB Rust Validator), you can deploy the official `kube-prometheus-stack`.

Run the following task to deploy Prometheus and Grafana into an isolated `monitoring` namespace:
```bash
task helm:monitor
```

Once deployed, retrieve the auto-generated Grafana admin password:
```bash
# For Linux / macOS:
kubectl get secret --namespace monitoring observability-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

# For Windows (PowerShell):
$secret = kubectl --namespace monitoring get secret observability-grafana -o jsonpath="{.data.admin-password}"; [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secret))
```

Finally, expose the Grafana dashboard to your local machine:
```bash
kubectl port-forward svc/observability-grafana 3000:80 -n monitoring
```

Visit http://localhost:3000 and use admin along with the decrypted password to access the Kubernetes compute resource dashboards.

## End-to-End Verification

**1. The K6 Stress Test**
Blast the API with high-concurrency traffic to watch the HPA auto-scaler in action.
```bash
k6 run tests/fixtures/loadtest.js
```
*Monitor the autoscaler scaling the API from 1 to 5 replicas dynamically: `kubectl get hpa -n sentinel-namespace -w`*

**2. Verify AI Persistence:**
Directly query the database to confirm the AI assigned a risk score:

```bash
kubectl exec -it -n sentinel-namespace $(kubectl get pods -n sentinel-namespace -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- psql -U sentinel -d sentinel_db -c "SELECT transaction_id, risk_score, created_at FROM transactions ORDER BY created_at DESC LIMIT 5;"
```

## Teardown
Once finished, completely remove the Helm release and clean up all associated resources:
```bash
task helm:off
```
