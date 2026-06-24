# Sentinel: GitOps & Continuous Deployment

*Fully autonomous GitOps pipeline utilizing ArgoCD and Jenkins for deterministic, zero-touch Kubernetes deployments.*

## Deployment Pipeline
The infrastructure relies on a single source of truth (GitHub) and eliminates local, fragmented deployment scripts.

**Workflow:** `Git Push` ➔ `Jenkins CI (Build & Push)` ➔ `Auto-Update Manifests` ➔ `ArgoCD Sync` ➔ `K8s Rollout`

## Architectural Decisions

| Component | Strategy & Rationale |
| :--- | :--- |
| **Image Registry** | **GHCR Integration:** Abandoned manual `local-dev` image loading. All services are built via Jenkins, tagged with exact Git commit SHAs, and pushed to GitHub Container Registry. |
| **ML Artifacts** | **Image Baking:** Instead of provisioning S3/MinIO for a lightweight (160 KB) XGBoost ONNX model, artifacts are explicitly baked into the consumer container during CI to eliminate operational overhead. |
| **CI/CD Handshake** | **Automated Manifests:** Jenkins pushes images, autonomously updates `values.yaml` via targeted `sed` commands, and commits back with a `[skip ci]` flag to prevent build loops. |
| **State Sync** | **ArgoCD Reconciliation:** ArgoCD continuously monitors the repository. Upon detecting Jenkins' commits, it pulls updated Helm manifests and GHCR images, gracefully rolling out immutable pods. |

## Post-Mortem & Incident Resolutions

During integration, the following critical roadblocks were isolated and resolved:

### 1. Remote State Enforcement (`ErrImageNeverPull`)
* **Symptom:** Initial ArgoCD deployments failed on consumer pods.
* **Root Cause:** Pods were configured with `imagePullPolicy: Never` targeting Docker Desktop caches. ArgoCD strictly enforces remote state, bypassing local caching.
* **Resolution:** Removed local dependencies, enforced GHCR registry URLs, and updated policy to `imagePullPolicy: IfNotPresent`.

### 2. Jenkins Variable Interpolation (`invalidimagename`)
* **Symptom:** Kubernetes rejected deployments with `invalidimagename` after Jenkins updated the Helm manifests.
* **Root Cause:** Jenkins Groovy script utilized `${IMAGE_TAG}` instead of `${env.IMAGE_TAG}` in the `sed` command, injecting empty strings into `values.yaml`.
* **Resolution:** Corrected Groovy environment syntax and refined the regex logic to accurately target `ghcr.io/` prefixed URLs.

### 3. Dynamic ML Artifact Resolution
* **Symptom:** AI Consumer crashed (`CrashLoopBackOff`) with `Model or Scaler not found`.
* **Root Cause:** The training pipeline exported timestamped ONNX files (e.g., `fraud_xgboost_20260604.onnx`), but inference logic was hardcoded to a static filename. Additionally, `.gitignore` was initially blocking `.onnx` files from the build context.
* **Resolution:** 1. Whitelisted ML artifacts in `.gitignore`.
  2. Refactored Python inference logic using `pathlib` and `glob` to dynamically scan `/app/models` and load the latest `*.onnx` file at runtime, decoupling code from rigid naming conventions.
