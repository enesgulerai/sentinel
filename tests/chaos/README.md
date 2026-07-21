# Sentinel - Chaos Engineering

This directory contains Chaos Engineering scenarios to test the resiliency, self-healing capabilities, and fault tolerance of the Sentinel project. The experiments are powered by [Chaos Mesh](https://chaos-mesh.org/).

## Prerequisites
Before running the chaos scenarios, ensure Chaos Mesh is installed in your Kubernetes cluster.

### Installation
Run the following commands to install Chaos Mesh using Helm:

```bash
helm repo add chaos-mesh [https://charts.chaos-mesh.org](https://charts.chaos-mesh.org)
helm repo update

# For Windows (PowerShell), run as a single line
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh --create-namespace --set dashboard.create=true --set dashboard.securityMode=false
```

## Available Scenarios

### 1. API Pod Kill (api-pod-kill.yaml)
Simulates a critical infrastructure failure by instantly terminating 50% of the API Gateway pods. This test validates the Horizontal Pod Autoscaler (HPA) response time and zero-downtime capabilities under load.

**To execute:**
```bash
kubectl apply -f api-pod-kill.yaml
```

### 2. Network Delay (api-network-delay.yaml)
Injects a 2000ms (2-second) network latency into all inbound and outbound traffic of the API pods. This validates timeout configurations and prevents cascading failures across the microservices architecture.

**To execute:**
```bash
kubectl apply -f api-network-delay.yaml
```

## Cleanup
To stop an active chaos experiment and restore the system to its normal state, delete the applied configuration:

```bash
kubectl delete -f api-pod-kill.yaml
kubectl delete -f api-network-delay.yaml
```
