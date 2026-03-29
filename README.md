# Real-Time AI Fraud Detection
Sentinel is an enterprise-grade, real-time fraud detection system. It simulates high-throughput financial transactions via streaming (Redpanda/Kafka) and evaluates them in milliseconds using an optimized ONNX inference engine.

---

## If You're a Data Scientist
The foundation of this project is built on strict data science principles, avoiding common pitfalls of highly imbalanced datasets (Fraud ratio: 0.17%).

If you want to explore the model engineering phase, navigate to the `experiments/` directory.

### 1. Data Processing
* Applies `RobustScaler` to numerical columns to handle extreme outliers without squashing the transaction variance.
* Strips unnecessary structures to prepare for raw array inputs.

### 2. Model Benchmarking
We don't guess; we benchmark. The evaluation strictly avoids "Accuracy" and focuses on **PR-AUC** and **Inference Latency**.

| Model | PR-AUC | Recall | Precision | F1-Score | Inference Time |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **XGBoost** | **0.8752** | **0.8469** | **0.8925** | **0.8691** | **0.0011 ms/row** |
| LightGBM | 0.8724 | 0.8571 | 0.8485 | 0.8528 | 0.0023 ms/row |
| Random Forest | 0.8501 | 0.7449 | 0.9605 | 0.8391 | 0.0025 ms/row |

*XGBoost was selected as the champion model due to its superior PR-AUC and sub-millisecond inference speed.*

### 3. Production Export
The champion XGBoost model is trained on the full dataset with calculated `scale_pos_weight` and exported to the **ONNX** format.
* **Final Model Size:** 176.47 KB (Optimized for microservices and RAM efficiency).