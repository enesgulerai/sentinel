# Sentinel Local Infrastructure (Helm)

This directory contains the Helm manifests designed to autonomously deploy all independent components of the Sentinel project (pgvector-supported Postgres, Redis, Redpanda, Go API, Rust Validator, and Asynchronous Python ML Consumer) as a single, unified system in a local Kubernetes environment.

## Quick Start

Follow these steps to bootstrap the entire system from scratch in your local Kubernetes environment (Docker Desktop K8s, Minikube, etc.).

### 1. Prerequisite: Build the Local ML Image
To ensure the Consumer image containing the machine learning models (`.onnx`, `.joblib`) is correctly utilized by Kubernetes locally (bypassing the remote registry via `imagePullPolicy: Never`), build and cache the image from the project root:

```bash
    docker build -f docker/consumer/Dockerfile -t sentinel-consumer:local-dev .
```

### 2. Deployment
Deploy the infrastructure into an isolated namespace and start all services with a single command:
```bash
    cd infrastructure/helm
    helm upgrade --install sentinel-prod ./sentinel -n sentinel-namespace --create-namespace
```

### 3. Monitoring
Watch all pods transition to the Running state in real-time (this typically takes 1-2 minutes):
```bash
    kubectl get pods -n sentinel-namespace -w
```
*Tail the logs to watch the asynchronous ML engine autonomously process validated data from the Redpanda queue:*
```bash
    kubectl logs -l app=sentinel-consumer -n sentinel-namespace -f
```

### 4. Teardown
To cleanly remove the entire system without leaving any dangling resources behind:
```bash
    helm uninstall sentinel-prod -n sentinel-namespace
```
