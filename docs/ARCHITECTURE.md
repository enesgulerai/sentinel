## Kubernetes Orchestration & Workload

Sentinel provides streamlined `Taskfile` commands for local Kubernetes orchestration. The automated setup provisions a multi-node cluster and configures strict workload isolation (Taints, Tolerations, and Node Affinity) to eliminate resource contention between the heavy AI inference engine and stateful data stores.

### Advanced Kubernetes Scheduling: Solving the "Noisy Neighbor" Problem

In our pursuit of highly optimized performance and sub-millisecond tail latencies, we encountered the classic "Noisy Neighbor" problem within our initial Single-Node setup. Running our lightweight, high-throughput Go API alongside I/O-intensive datastores (Postgres/Redpanda/Redis) and a CPU-hungry XGBoost AI inference engine (Consumer) created severe resource contention. Whenever the AI model spiked to 100% CPU utilization, the Go API and Redis suffered from instantaneous latency spikes.

To achieve strict resource isolation, we evolved the architecture to a **Multi-Node Cluster** (1 Control Plane, 2 Workers) and implemented advanced Kubernetes scheduling strategies:

#### 1. Storage Isolation via Node Affinity
* **Strategy:** We labeled one of our worker nodes strictly for stateful workloads (`role=storage`).
* **Implementation:** We applied **Node Affinity** rules to the Postgres, Redis, and Redpanda manifests.
* **Result:** Kubernetes is now forced to schedule these stateful components exclusively on the storage node. Disk I/O operations are highly centralized, guaranteeing they never bottleneck the API or AI compute layers.

#### 2. AI Inference Quarantine via Taints & Tolerations
* **Strategy:** We tainted our second worker node (`dedicated=ai-inference:NoSchedule`), essentially hanging a "Do Not Enter" sign for standard workloads.
* **Implementation:** We equipped our heavy Python Consumer manifest with the exact **Tolerations** required to bypass this taint.
* **Result:** The XGBoost inference model now operates in absolute quarantine. No other pods (such as the Go API or databases) can be scheduled on this node. The AI engine can freely consume 100% of its node's CPU without causing a single millisecond of latency degradation to the rest of the ecosystem.
