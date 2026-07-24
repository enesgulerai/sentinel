# Sentinel LocalStack Infrastructure (Terraform)

This directory contains the local emulation of the AWS S3 infrastructure, where "Cold Data" and Audit Logs are stored within Sentinel's Event-Driven architecture.

We use [LocalStack](https://localstack.cloud/) to test our Infrastructure as Code (IaC) locally before provisioning real AWS services in the cloud.

## Architectural Decision: Why S3?
High-volume raw transaction data (tens of thousands per second) coming into Sentinel is split into two paths:
1. **Hot Data (PostgreSQL):** Processed data that has passed through the Rust validator and Python ML engine to calculate the risk score.
2. **Cold Data (AWS S3 - Audit Logs):** The **raw, untouched** payload exactly as received by the Go API. It is asynchronously dumped into S3 (Fire and Forget) for regulatory compliance, audit trails, and future ML model training.

---

## Deployment Guide

Before running any Terraform commands, Sentinel's Kubernetes environment (including LocalStack) **must** be deployed via Helm.

### Step 1: Spin up the Cluster
Use the `Taskfile` command in the root directory to start the Kubernetes environment:
```bash
task helm:on
```
*(This command will spin up NGINX Ingress, Redpanda, Valkey, PostgreSQL, Go, Rust, Python, and LocalStack pods.)*

### Step 2: Open LocalStack Tunnel
Open a temporary tunnel so Terraform can reach LocalStack inside the cluster (Leave this terminal open):
```bash
kubectl port-forward -n sentinel-namespace svc/localstack 4566:4566
```

### Step 3: Apply Terraform
Navigate to this directory (`infrastructure/terraform/localstack`) and build the infrastructure:
```bash
# Initialize Terraform and download plugins
terraform init

# Create the S3 bucket and configurations
terraform apply -var="environment=local" -auto-approve
```
Upon success, you will see the message `Apply complete! Resources: 2 added`.

### Step 4: Verify Connection
Query LocalStack using the AWS CLI to test if the S3 bucket was successfully created:
```bash
aws --endpoint-url=http://localhost:4566 s3 ls
```

---

## Troubleshooting

**1. "Error: creating S3 Bucket... timeout"**
Terraform might freeze due to resource constraints in the LocalStack Community edition. In this case, abort the process (`Ctrl+C`), clear Terraform's locked state, and try again:
```bash
Remove-Item -Path "terraform.tfstate*" -Force  # Windows (PowerShell)
# rm -rf terraform.tfstate*                    # Linux/Mac
terraform apply -var="environment=local" -auto-approve
```

**2. Port-Forward "forcibly closed" Warning**
`kubectl` might throw this warning because the AWS CLI or Terraform aggressively closes the TCP connection after completing its task. This is a harmless log; your tunnel is still up and running.
