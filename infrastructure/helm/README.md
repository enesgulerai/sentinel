# Sentinel: Local Infrastructure & Helm Workloads

*Infrastructure as Code (IaC) configurations for deploying Sentinel's isolated microservices (Go API, Rust Validator, Python ML Consumer) and stateful datastores.*

## Resource Isolation & Scheduling Strategy

To achieve sub-millisecond tail latencies and prevent "noisy neighbor" degradation under 14,500+ RPS, the cluster enforces strict scheduling policies:

| Strategy | Implementation | Operational Impact |
| :--- | :--- | :--- |
| **Storage Isolation** | Node Affinity | Forces I/O-heavy stores (Postgres, Dragonfly Redis, Redpanda) onto dedicated storage nodes. |
| **AI Quarantine** | Taints & Tolerations | Isolates the CPU-intensive XGBoost inference engine. Guarantees 100% core utilization without degrading the Go API latency. |
| **Zero-Waste Scaling** | HPA (Horizontal Pod Autoscaler) | Dynamically clones the stateless Go API (capped at 256Mi memory limit) to absorb high-throughput traffic spikes. |

## Deployment Lifecycle

```bash
task helm:on       # Provision unified Helm chart (Single Source of Truth)
task helm:status   # Watch pod transitions (Wait for Postgres/Redpanda quorum)
task helm:forward  # Bind K8s network to local machine (Leave terminal open)
task helm:off      # Teardown release and purge cluster resources
```

## Observability Stack
Deploy the `kube-prometheus-stack` to monitor real-time health, HPA metrics, and the ultra low footrpint of the core services (~15MB Go API, ~3MB Rust Validator).

```bash
# 1. Deploy Prometheus & Grafana
task helm:monitor

# 2. Retrieve Grafana Admin Password
# Linux/macOS:
kubectl get secret -n monitoring observability-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
# Windows (PowerShell):
$secret = kubectl -n monitoring get secret observability-grafana -o jsonpath="{.data.admin-password}"; [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secret))

# 3. Access Dashboard (http://localhost:3000)
kubectl port-forward svc/observability-grafana 3000:80 -n monitoring
```

## End-to-End Load Testing & HPA Verification

### 1. Enable Local HPA (Metrics Server Patch)
For local environments (e.g., Kind) bypass TLS validation to allow Kubernetes to scrape CPU/RAM metrics and trigger the HPA. Run via Powershell:

```powershell
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
Set-Content -Path patch.json -Value '[{ "op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls" }]'
kubectl patch -n kube-system deployment metrics-server --type=json --patch-file patch.json
Remove-Item -Path patch.json -Force
```

### 2. Execute Stress Test
Once metrics-server is active (wait ~60s), blast the API and monitor dynamic scaling.

```bash
# Terminal 1: Run the K6 Load Test
k6 run tests/fixtures/loadtest.js

# Terminal 2: Watch HPA scale the API (1 to 5 replicas dynamically)
kubectl get hpa -n sentinel-namespace -w
```

### 3. Verify AI Persistence
Confirm the pipeline processed the traffic and assigned risk scores correctly:

```bash
kubectl exec -it -n sentinel-namespace $(kubectl get pods -n sentinel-namespace -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- psql -U sentinel -d sentinel_db -c "SELECT transaction_id, risk_score, created_at FROM transactions ORDER BY created_at DESC LIMIT 5;"
```
