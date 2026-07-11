# Sentinel: AWS FinOps & Cost Optimization

*Production-grade Terraform manifests and Infracost analysis demonstrating a 73% infrastructure cost reduction while sustaining 25,300+ RPS at sub-7ms latency.*

## FinOps Impact Summary

| Metric | Baseline (Managed) | Optimized (In-Cluster) | Delta |
| :--- | :--- | :--- | :--- |
| **Monthly Cost** | ~$452.00 | **$120.77** | **-73%** |
| **Throughput** | 25,300+ RPS | 25,300+ RPS | 0% (No degradation) |
| **Tail Latency** | < 7ms | < 7ms | 0% (No degradation) |

## Optimization Strategy

The financial bottleneck was eliminated by pivoting from a "lift and shift" managed service model to an aggressively tuned, resource-capped Kubernetes architecture.

### 1. Eliminating the Managed Service Premium
* **Legacy Setup:** Relied heavily on AWS RDS (PostgreSQL), ElastiCache (Redis), and 3 dedicated EC2 instances for Redpanda.
* **Action:** Purged managed services from `datastores.tf`. Migrated all stateful workloads directly into the EKS cluster as isolated Helm pods, completely bypassing managed service margins.
* **Baseline Infracost Report:**
  ![Sentinel AWS Before Optimized Cost Estimate](../../../docs/images/infrastructure/aws-451.png)

### 2. Guaranteed QoS & Resource Hard-Capping
* **Action:** Mapped P99 CPU and Max RAM utilization via Prometheus/cAdvisor to define millimeter-perfect `requests` and `limits`, achieving the **Guaranteed QoS class** across the stack.
* **Resource Footprint:**
  * **Go API Gateway:** Hardcapped at `600m CPU / 128Mi RAM`.
  * **Rust Validator:** Ultra-lightweight cap at `50m CPU / 16Mi RAM`.
* **Impact:** Zero CPU throttling, zero OOMKilled events, and the absolute elimination of idle compute waste.

### 3. Graviton ARM64 & Spot Instance Synergy
* **Action:** Capitalized on the ultra-low resource footprint of the memory-safe microservices (Go/Rust) by transitioning the entire EKS node group to **Graviton ARM64 (`t4g.medium`) Spot Instances**.
* **Impact:** Reduced compute baseline to just 2 nodes, drastically cutting hourly EC2 rates.

## Final Infracost Report ($121 Reality)

![Sentinel AWS Final Optimized Cost Estimate](../../../docs/images/infrastructure/aws-121.png)

* **EKS Control Plane:** $73.00/mo *(Fixed AWS Fee)*
* **2x `t4g.medium` Spot Nodes + EBS:** ~$47.77/mo
* **Total:** **$120.77 / month**
