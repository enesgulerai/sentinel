# Sentinel Local Infrastructure (Helm)

This directory contains the Helm manifests designed to autonomously deploy all independent components of the Sentinel project (pgvector-supported Postgres, Redis, Redpanda, Go API, Rust Validator, and Asynchronous Python ML Consumer) as a single, unified system in a local Kubernetes environment.

## Quick Start

Follow these steps to bootstrap the entire system from scratch in your local Kubernetes environment (Docker Desktop K8s, Minikube, etc.).

### 1. Deployment
Run the following command to automatically build the local ML image (bypassing the remote registry) and deploy the unified Helm chart into an isolated namespace:
```bash
    task helm:on
```

### 2. Monitoring
Watch all pods transition to the Running state in real-time (this typically takes 1-2 minutes):
```bash
    task helm:status
```
*Tail the logs to watch the asynchronous ML engine autonomously process validated data from the Redpanda queue:*
```bash
    kubectl logs -l app=sentinel-consumer -n sentinel-namespace -f
```

### 3. Teardown
Once finished, completely remove the Helm release and clean up all associated resources cleanly:
```bash
    task helm:off
```
