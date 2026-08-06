<div align="left">

# Sentinel: Enterprise Real-Time Fraud & Anomaly Ingestion Engine
### Module: LocalStack Infrastructure (Terraform)

</div>

---

## Overview
Infrastructure as Code (IaC) configurations for local emulation of AWS S3 using [LocalStack](https://localstack.cloud/). This module enables developers to test and validate Terraform manifests locally before provisioning real cloud services. It is responsible for managing Sentinel's "Cold Data" layer, focusing on immutable audit logs within the event-driven architecture.

## Architecture & Data Strategy

To maintain sub-millisecond latencies under high throughput (tens of thousands of RPS), incoming raw transactions are bifurcated into two distinct storage pathways:

### Core Mechanisms
*   **Hot Data Pathway (PostgreSQL):** Stores fully processed transaction data that has successfully passed through the Rust validator and Python ML engine, including the final calculated risk score.
*   **Cold Data Pathway (AWS S3 - Audit Logs):** Stores the **raw, untouched** payload exactly as received by the Go API Gateway. It is asynchronously dumped into S3 using a "fire-and-forget" pattern. This ensures regulatory compliance, provides immutable audit trails, and serves as the foundational data lake for future ML model training.
*   **Local Cloud Emulation:** Utilizes LocalStack within the Kubernetes cluster to achieve API parity with AWS S3, enabling robust local IaC testing with zero cloud expenditure.

## Prerequisites
Ensure the following tools and cluster configurations are active before provisioning the local infrastructure:
*   **[Kubernetes & Helm]:** Sentinel's unified Kubernetes environment must already be deployed (LocalStack pod must be running).
*   **[Terraform]:** Installed locally to execute the `.tf` manifests.
*   **[AWS CLI]:** Installed locally to query and verify the emulated AWS endpoints.

## Deployment & Provisioning

### 1. Spin up the Core Cluster
Before executing Terraform, the core infrastructure (including LocalStack, NGINX, Redpanda, Valkey, and Postgres) must be active. From the project root, execute:

```bash
task helm:on
```

### 2. Establish LocalStack Tunnel
Open a temporary network tunnel to allow the local Terraform runtime to communicate with the LocalStack pod inside the cluster. **(Leave this terminal open)**

```bash
kubectl port-forward -n sentinel-namespace svc/localstack 4566:4566
```

### 3. Apply Terraform Manifests
Navigate to this directory (`infrastructure/terraform/localstack`) and provision the S3 infrastructure:

```bash
# Initialize Terraform and download required providers
terraform init

# Provision the S3 bucket and configurations
terraform apply -var="environment=local" -auto-approve
```
*Expected Output: `Apply complete! Resources: 2 added`*

### 4. Verify Emulated Resources
Query the LocalStack API via the AWS CLI to confirm the successful creation of the S3 bucket:

```bash
aws --endpoint-url=http://localhost:4566 s3 ls
```

---

## Troubleshooting

| Error / Warning | Root Cause & Resolution |
| :--- | :--- |
| **"Error: creating S3 Bucket... timeout"** | Terraform may freeze due to resource constraints in the LocalStack Community edition. Abort (`Ctrl+C`), clear the locked state, and retry.<br><br>**Windows (PowerShell):** `Remove-Item -Path "terraform.tfstate*" -Force`<br>**Linux/Mac:** `rm -rf terraform.tfstate*`<br>Then re-run: `terraform apply -var="environment=local" -auto-approve` |
| **Port-Forward "forcibly closed" Warning** | `kubectl` may throw this if the AWS CLI or Terraform aggressively closes the TCP connection after completing its request. This is a harmless log; your tunnel remains active and healthy. |
