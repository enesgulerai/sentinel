# Sentinel: GitOps & Continuous Deployment Architecture

## Overview
This document outlines the transition of Project Sentinel's infrastructure from manual deployments to a fully autonomous GitOps model using **ArgoCD** and **Jenkins**. By treating infrastructure as code (IaC) and utilizing a single source of truth (GitHub), we established a deterministically reproducible, zero-touch deployment pipeline.

The architecture adheres to the engineering philosophy that "one whole is better than ten halves." Rather than maintaining fragmented local deployment scripts and manual image loading, the system is unified into a cohesive pipeline from code commit to cluster deployment.

## Architectural Decisions & Workflow

1. **GitHub Container Registry (GHCR) Integration:**
   Abandoned the `local-dev` image tagging and manual `kind load docker-image` workflows. All services (API, Validator, Consumer) are built via Jenkins CI, tagged with their exact Git commit SHA, and pushed to GHCR.
2. **Model Baking for AI Consumer:**
   Instead of introducing the operational overhead of AWS S3 or a local MinIO instance for a highly optimized, lightweight (160 KB) XGBoost ONNX model, the machine learning artifacts (model and robust scaler) are directly baked into the consumer container image during the CI build stage.
3. **Automated Manifest Updates (The CI/CD Handshake):**
   Jenkins is configured not only to build and push images but also to autonomously update the `values.yaml` file with the latest Git SHA using surgical `sed` commands. It then commits this change back to the repository using a `[skip ci]` flag to prevent infinite build loops.
4. **ArgoCD Synchronization:**
   ArgoCD continuously monitors the GitHub repository. Upon detecting the automated commit from Jenkins, it pulls the updated Helm manifests and the new GHCR images, gracefully rolling out the new pods while terminating the old ones.

## Challenges Faced & Engineering Solutions

During the integration phase, several critical roadblocks were encountered and resolved:

### 1. The Local Environment Illusion (`ErrImageNeverPull`)
* **Issue:** Initial ArgoCD deployments failed with `ErrImageNeverPull`. The consumer pod was instructed to use `imagePullPolicy: Never` and look for a `local-dev` image. However, the cluster context was set to Docker Desktop (Single-Node), and ArgoCD strictly enforces configurations from the remote repository, bypassing local Docker caches.
* **Solution:** Completely removed local image dependencies. Migrated to GHCR, enforcing `imagePullPolicy: IfNotPresent` and remote registry pulls.

### 2. Jenkins Groovy Variable Interpolation (`invalidimagename`)
* **Issue:** After configuring Jenkins to update `values.yaml`, Kubernetes rejected the consumer deployment with an `invalidimagename` error.
* **Root Cause:** The Jenkins Groovy script used `${IMAGE_TAG}` instead of `${env.IMAGE_TAG}` within the `sed` command, resulting in an empty string being written to the Helm values file. Additionally, the repository URL for the consumer lacked the `ghcr.io/...` prefix, causing a regex mismatch.
* **Solution:** Corrected the Groovy environment variable syntax and updated the Helm values to include the full GHCR registry URL, ensuring the `sed` command targets and updates the tags accurately.

### 3. Dynamic Model Path Resolution in Python
* **Issue:** The AI Consumer pod crashed in a `CrashLoopBackOff` state with the error: `Model or Scaler not found`. The training pipeline was exporting the ONNX model with a timestamped filename (e.g., `fraud_xgboost_20260604.onnx`), but the inference code was hardcoded to look for `fraud_xgboost.onnx`.
* **Root Cause:** The `.gitignore` file initially blocked `.onnx` files, resulting in empty directories being baked into the image. Even after fixing the `.gitignore`, the hardcoded filename mismatch persisted.
* **Solution:** Refactored the Python consumer code to utilize the `pathlib` and `glob` libraries. The consumer now dynamically scans the `/app/models` directory for any `*.onnx` file and automatically loads the latest one, decoupling the inference engine from rigid filename structures.

## System State
The current GitOps pipeline is fully operational. A single `git push` of application code or a new model triggers the CI pipeline, builds the artifacts, updates the infrastructure manifests, and synchronizes the cluster via ArgoCD with zero manual intervention.
