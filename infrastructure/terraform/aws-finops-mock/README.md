<div align="left">

# Sentinel: Enterprise Real-Time Fraud & Anomaly Ingestion Engine
### Module: AWS FinOps, IaC Security & Cost Optimization

</div>

---

## Overview
Production-grade Terraform manifests and Infracost analysis demonstrating an 85% infrastructure cost reduction while sustaining 25,300+ RPS at sub-7ms latency. The financial bottleneck was eliminated by pivoting from an unoptimized "lift and shift" managed service model to an aggressively tuned, structurally secure Kubernetes architecture.

## FinOps Impact Summary

| Metric | Baseline (Unoptimized) | Optimized (Current) | Delta |
| :--- | :--- | :--- | :--- |
| **Monthly Cost** | ~$744.00 | **$107.00** | **-85%** |
| **Throughput** | 25,300+ RPS | 25,300+ RPS | 0% (No degradation) |
| **Tail Latency** | < 7ms | < 7ms | 0% (No degradation) |

## Optimization & Architecture Strategy

### Core Mechanisms
*   **Network & Managed Service Purge:** Eliminated expensive NAT Gateway overhead (~$35/mo) by optimizing traffic routing. Purged managed datastores (PostgreSQL, ElastiCache) and migrated workloads directly into the EKS cluster as isolated Helm pods, replacing heavy Redis deployments with the highly efficient **Valkey**.
*   **Escaping CFS Throttling (The CPU Limit Epiphany):** Shifted from a "Guaranteed QoS" model to a **Burstable QoS** model. By strictly defining resource `requests` for millimeter-perfect pod scheduling but **intentionally omitting CPU limits**, microservices (Go/Rust) can now burst into idle node CPU cycles. This eliminated artificial Linux Kernel CFS quota throttling, OOMKilled events, and idle compute waste.
*   **Graviton ARM64 & Spot Instance Synergy:** Capitalized on the ultra-low resource footprint of our memory-safe microservices by transitioning the entire EKS node group to **Graviton ARM64 (`t4g.medium`) Spot Instances**. This delivered up to 40% better price-performance over x86 and reduced our compute baseline to ~$32/month.
*   **IaC Security via Bridgecrew Checkov:** Integrated **Checkov** into both the local `.pre-commit-config.yaml` and GitHub Actions pipeline. Enforced KMS keys for secure encryption and enabled CloudWatch Log Groups. Every Terraform configuration is continuously scanned, ensuring exposed S3 buckets, missing VPC Flow Logs, and misconfigured Security Groups are blocked before deployment.

## Infracost Evidence: Before vs. After

### Baseline Architecture (~$744 / month)
*The original managed-service heavy architecture cost breakdown.*

![Sentinel AWS Before Optimized Cost Estimate](../../../docs/images/infracost-report/infracost-744.png)

### Optimized Architecture (~$107 / month)
*The current Graviton-powered, in-cluster optimized cost breakdown.*

![Sentinel AWS Final Optimized Cost Estimate](../../../docs/images/infracost-report/infracost-107.png)

*   **EKS Control Plane:** $73.00/mo *(Fixed AWS Fee)*
*   **Graviton Spot Nodes + EBS:** ~$32.87/mo
*   **KMS & CloudWatch Security:** ~$1.00/mo
*   **Total:** **~$107.00 / month**
