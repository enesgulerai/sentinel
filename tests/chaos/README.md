# Sentinel - Chaos Engineering

This directory contains Chaos Engineering scenarios to test the resiliency, self-healing capabilities, and fault tolerance of the Sentinel project. The experiments are powered by [Chaos Mesh](https://chaos-mesh.org/) and validated using k6 load tests.

## Continuous Integration (CI)
Chaos scenarios are fully automated. The `.github/workflows/chaos-test.yaml` pipeline runs automatically every night at 02:00. It provisions a KinD cluster, deploys the infrastructure, injects all chaos scenarios below, and runs a k6 load test to ensure the system survives the impact.

## Prerequisites
Before running the chaos scenarios manually, ensure Chaos Mesh and its Custom Resource Definitions (CRDs) are installed in your Kubernetes cluster.

### Installation
Run the following commands to install the CRDs and Chaos Mesh using Helm:

```bash
# 1. Install all CRDs (Required for StressChaos)
kubectl apply -f https://mirrors.chaos-mesh.org/latest/crd.yaml

# 2. Install Chaos Mesh
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update

# For Windows (PowerShell), run as a single line:
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh --create-namespace --set dashboard.create=true --set dashboard.securityMode=false
```

## Available Scenarios

### 1. API Pod Kill (`api-gateway-pod-kill.yaml`)
Simulates a critical infrastructure failure by instantly terminating 50% of the API pods. This test validates the Horizontal Pod Autoscaler (HPA) response time and zero-downtime capabilities.

### 2. Network Delay (`api-network-delay.yaml`)
Injects a 2000ms (2-second) network latency into all inbound and outbound traffic of the API pods. Validates timeout configurations and prevents cascading failures.

### 3. CPU Stress (`api-cpu-stress.yaml`)
Injects 100% CPU load into the API pods to test system limits. Validates that the absence of CPU limits in the deployment allows the pods to burst without triggering CFS throttling.

### 4. Redis Network Loss (`redis-network-loss.yaml`)
Simulates a complete network partition between the API and the Redis cache (100% packet loss). Validates the application's graceful degradation and fallback mechanisms.

**To execute any scenario manually:**
```bash
kubectl apply -f <scenario-file.yaml>
```

## Cleanup
To stop an active chaos experiment and restore the system to its normal state, delete the applied configuration:

```bash
kubectl delete -f api-gateway-pod-kill.yaml
kubectl delete -f api-network-delay.yaml
kubectl delete -f api-cpu-stress.yaml
kubectl delete -f redis-network-loss.yaml
```
