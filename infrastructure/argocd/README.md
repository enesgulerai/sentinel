<div align="left">

# Sentinel: Enterprise Real-Time Fraud & Anomaly Ingestion Engine
### Module: GitOps & Continuous Deployment

</div>

---

## Overview
This module governs the fully autonomous GitOps pipeline for the Sentinel platform, utilizing ArgoCD and Jenkins for deterministic, zero-touch Kubernetes deployments. By establishing the repository as the single source of truth, it entirely eliminates the need for local, fragmented deployment scripts and ensures production environments strictly mirror version-controlled state.

## Architecture & Workflow

### Deployment Pipeline
**Workflow:** `Git Push` ➔ `Jenkins CI (Build & Push)` ➔ `Auto-Update Manifests` ➔ `ArgoCD Sync` ➔ `K8s Rollout`

### Architectural Decisions

| Component | Strategy & Rationale |
| :--- | :--- |
| **Image Registry** | **GHCR Integration:** Abandoned manual `local-dev` image loading. All services are built via Jenkins, tagged with exact Git commit SHAs, and pushed to GitHub Container Registry. |
| **ML Artifacts** | **Image Baking:** Instead of provisioning S3/MinIO for a lightweight (160 KB) XGBoost ONNX model, artifacts are explicitly baked into the consumer container during CI to eliminate operational overhead. |
| **CI/CD Handshake** | **Automated Manifests:** Jenkins pushes images, autonomously updates `values.yaml` via targeted `sed` commands, and commits back with a `[skip ci]` flag to prevent build loops. |
| **State Sync** | **ArgoCD Reconciliation:** ArgoCD continuously monitors the repository. Upon detecting Jenkins' commits, it pulls updated Helm manifests and GHCR images, gracefully rolling out immutable pods. |

## Prerequisites
To operate and monitor this automated deployment pipeline, ensure the following infrastructure is provisioned:
*   **Kubernetes Cluster:** EKS or a local equivalent (KinD, Minikube).
*   **ArgoCD:** Installed and configured within the cluster to monitor the repository.
*   **Jenkins CI:** Configured with webhooks to detect repository pushes.
*   **GitHub Container Registry (GHCR):** Authenticated for image pushing and pulling.

## Quick Start & Usage
Because this is a zero-touch GitOps pipeline, deployments are fully automated and do not require manual execution commands under normal circumstances.

1.  Merge or push your code changes to the `main` branch.
2.  Jenkins will automatically trigger the build, push images to GHCR, and update the Helm `values.yaml`.
3.  ArgoCD will detect the state change in the repository and automatically sync the Kubernetes cluster.

*(Optional)* You can manually monitor the synchronization status via the ArgoCD CLI:
```bash
argocd app sync sentinel-app
argocd app get sentinel-app
```

## Post-Mortem & Troubleshooting
During the integration phase, the following critical roadblocks were isolated and resolved. These serve as a historical reference for debugging deployment state issues:

### 1. Remote State Enforcement (`ErrImageNeverPull`)
*   **Symptom:** Initial ArgoCD deployments failed on consumer pods.
*   **Root Cause:** Pods were configured with `imagePullPolicy: Never` targeting Docker Desktop caches. ArgoCD strictly enforces remote state, bypassing local caching.
*   **Resolution:** Removed local dependencies, enforced GHCR registry URLs, and updated policy to `imagePullPolicy: IfNotPresent`.

### 2. Jenkins Variable Interpolation (`invalidimagename`)
*   **Symptom:** Kubernetes rejected deployments with `invalidimagename` after Jenkins updated the Helm manifests.
*   **Root Cause:** Jenkins Groovy script utilized `${IMAGE_TAG}` instead of `${env.IMAGE_TAG}` in the `sed` command, injecting empty strings into `values.yaml`.
*   **Resolution:** Corrected Groovy environment syntax and refined the regex logic to accurately target `ghcr.io/` prefixed URLs.

### 3. Dynamic ML Artifact Resolution
*   **Symptom:** AI Consumer crashed (`CrashLoopBackOff`) with `Model or Scaler not found`.
*   **Root Cause:** The training pipeline exported timestamped ONNX files (e.g., `fraud_xgboost_20260604.onnx`), but inference logic was hardcoded to a static filename. Additionally, `.gitignore` was initially blocking `.onnx` files from the build context.
*   **Resolution:**
    1. Whitelisted ML artifacts in `.gitignore`.
    2. Refactored Python inference logic using `pathlib` and `glob` to dynamically scan `/app/models` and load the latest `*.onnx` file at runtime, decoupling code from rigid naming conventions.
