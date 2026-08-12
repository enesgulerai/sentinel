<div align="left">

# Sentinel: Enterprise Real-Time Fraud & Anomaly Ingestion Engine
### Module: Infrastructure & Helm Workloads (IaC)

</div>

---

## Overview
Infrastructure as Code (IaC) and Kubernetes orchestration manifests for deploying Sentinel's isolated microservices (Go API Gateway, Rust Validator, Python ML Consumer) alongside high-performance stateful datastores. Engineered for sub-millisecond tail latencies and deterministic resource isolation under high-throughput conditions (25,300+ RPS).

## Architecture & Scheduling Strategy

### Core Mechanisms
*   **Kernel-Level Network Optimization:** Replaces legacy `kube-proxy` iptables routing with **Cilium (eBPF)** to eliminate CPU bottlenecks and guarantee $O(1)$ packet routing latency at the Linux kernel layer.
*   **Strict Resource Isolation:** Utilizes Kubernetes Node Affinity and Taints/Tolerations to isolate compute-bound ML inference jobs from latency-critical HTTP ingestion pathways.
*   **Dynamic Horizontal Autoscaling:** Configures Horizontal Pod Autoscalers (HPA) to scale stateless ingress workers based on real-time CPU/RAM utilization metrics.
*   **Zero-Instrumentation Observability:** Integrates `kube-prometheus-stack` and Cilium Hubble for L3/L4 and L7 real-time service mapping and metric aggregation.

### Resource Scheduling Policies

| Strategy | Implementation | Operational Impact |
| :--- | :--- | :--- |
| **Storage Isolation** | Node Affinity | Forces I/O-heavy datastores (Postgres, Dragonfly Redis, Redpanda) onto dedicated storage nodes. |
| **AI Quarantine** | Taints & Tolerations | Isolates the CPU-intensive XGBoost inference engine. Guarantees 100% core utilization without degrading Go API latency. |
| **Zero-Waste Scaling** | HPA (Horizontal Pod Autoscaler) | Dynamically clones the stateless Go API (capped at 256Mi memory limit) to absorb high-throughput traffic spikes. |

## Prerequisites
Ensure the following tools and cluster configurations are active before deploying the infrastructure:
*   **[Kubernetes Cluster]:** Docker Desktop K8s, Kind, or Minikube.
*   **[Helm v3]:** Package manager for Kubernetes workload orchestration.
*   **[Task Runner]:** `task` CLI installed for executing deployment lifecycles.
*   **[k6]:** Load testing tool for high-concurrency verification.

## Deployment Lifecycle & Operations
All infrastructure lifecycle tasks are wrapped inside the unified `Taskfile` interface.

```bash
# Provision unified Helm chart (Single Source of Truth)
task helm:dev

# Watch pod transitions and wait for datastore quorum
task helm:status

# Bind K8s network services to local host interfaces
task helm:forward

# Teardown release and purge cluster resources
task helm:off
```

## Observability & Networking (eBPF & Cilium)

### 1. Prometheus & Grafana Stack
Deploy the observability suite to monitor footprint metrics (~65MB Go API, ~19MB Rust Validator) and HPA behavior.

```bash
# 1. Deploy Prometheus & Grafana stack
task helm:monitor

# 2. Retrieve Grafana Admin Password (Linux/macOS)
kubectl get secret -n monitoring observability-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

# 3. Access Grafana Dashboard (http://localhost:3000)
kubectl port-forward svc/observability-grafana 3000:80 -n monitoring
```

### 2. Cilium eBPF CNI & Hubble UI
Bootstrap the cluster in eBPF mode for high-throughput packet routing and live visual service mapping.

```bash
# Add Cilium Helm repository
helm repo add cilium https://helm.cilium.io/
helm repo update

# Install Cilium in eBPF mode (replacing kube-proxy)
helm install cilium cilium/cilium --namespace kube-system --set kubeProxyReplacement=true

# Enable Hubble Relay and UI Dashboard
helm upgrade cilium cilium/cilium --namespace kube-system --reuse-values --set hubble.relay.enabled=true --set hubble.ui.enabled=true

# Access Hubble Visual Dashboard (http://localhost:12000)
kubectl port-forward -n kube-system svc/hubble-ui 12000:80
```

## End-to-End Load Testing & Verification

### 1. Enable Local HPA (Metrics Server Patch)
Local development clusters require bypassing TLS verification to enable metric scraping for HPA triggers.

```powershell
# Install Metrics Server for HPA
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch Metrics Server to allow insecure TLS for local development
Set-Content -Path patch.json -Value '[{ "op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls" }]'
kubectl patch -n kube-system deployment metrics-server --type=json --patch-file patch.json
Remove-Item -Path patch.json -Force
```

### 2. Concurrency Stress Test & Persistence Check
Execute the load test scenario and verify dynamic pod replication alongside database persistence.

```bash
# Terminal 1: Run the K6 Load Test
k6 run tests/fixtures/loadtest.js

# Terminal 2: Watch HPA scale the API (1 to 5 replicas dynamically)
kubectl get hpa -n sentinel-namespace -w

# Terminal 3: Verify processed risk scores in PostgreSQL
kubectl exec -it -n sentinel-namespace $(kubectl get pods -n sentinel-namespace -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- psql -U sentinel_user -d sentinel_db -c "SELECT transaction_id, risk_score, created_at FROM transactions ORDER BY created_at DESC LIMIT 5;"
```

## Configuration & Task Reference

| Command / File | Target Domain | Description |
| :--- | :--- | :--- |
| `values.yaml` | Helm Chart | Default development configurations, resource requests, and ingress rules. |
| `values.production.yaml` | Helm Chart | Production override values managed dynamically by the GitOps CD pipeline. |
| `task helm:on` | Infrastructure | Deploys the main `sentinel` Helm release. |
| `task helm:prod` | Infrastructure | Deploys the production workloads via `values.production.yaml`. |
| `task helm:monitor` | Observability | Provisions the `kube-prometheus-stack` monitoring namespace. |
