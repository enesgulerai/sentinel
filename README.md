<div align="left">

# Sentinel: Real-Time AI Fraud Detection

*Enterprise-grade, event-driven anomaly detection pipeline with sub-millisecond ONNX inference.*

![Python](https://img.shields.io/badge/python-000000?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=for-the-badge&logo=fastapi&logoColor=009688)
![Docker](https://img.shields.io/badge/docker-000000?style=for-the-badge&logo=docker&logoColor=2496ED)
<br>
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-000000?style=for-the-badge&logo=apachekafka&logoColor=white)
![Redis](https://img.shields.io/badge/redis-000000?style=for-the-badge&logo=redis&logoColor=FF4438)
![Prefect](https://img.shields.io/badge/Prefect-000000?style=for-the-badge&logo=prefect&logoColor=2670FF)
![Trivy](https://img.shields.io/badge/Trivy-000000?style=for-the-badge&logo=aquasecurity&logoColor=1904DA)
![Bandit](https://img.shields.io/badge/Bandit-000000?style=for-the-badge&logo=python&logoColor=ffdd54)
![Taskfile](https://img.shields.io/badge/Taskfile-000000?style=for-the-badge&logo=task&logoColor=29BEB0)

</div>

---
**Sentinel** is an enterprise-grade, real-time fraud detection system. It simulates high-throughput financial transactions via streaming (Redpanda/Kafka) and evaluates them in milliseconds using an optimized ONNX inference engine.

## Quick Start

### 1. Clone the Repository
Clone the project to your local machine and navigate into the root directory:

```bash
    git clone https://github.com/enesgulerai/sentinel.git
    cd sentinel
```

### 2. Configure Environment Variables
The data ingestion process requires a Google Drive File ID to fetch the raw dataset via gdown. Copy the example environment file to create your local configuration:

```bash
    cp .env.example .env
```

### 3. Install Dependencies
Install all required Python packages and set up the local development environment. This command utilizes `uv` to create a virtual environment and strictly syncs the dependencies locked in `uv.lock`.

```bash
    task install
```

### 4. Execute the ML Pipeline
Run the complete machine learning pipeline. This automated task will fetch the raw dataset using your provided `.env` variable, apply preprocessing transformations, and train the baseline model.

```bash
    task pipeline
```

### 5. Launch the Application (Docker Compose)
Start the Docker containers to spin up the Prefect orchestration server, API gateway, and all other core services in detached mode.

```bash
    task up
```

## Local Services & Ports

Once the Docker containers are up and running, you can access the core services via the following local addresses:

| Service | Local URL |
| :--- | :--- |
| **Prefect Dashboard** | http://localhost:4200 |
| **API Gateway** | http://localhost:8000 |
| **Redpanda Console** | http://localhost:8080 |
| **Streamlit UI** | http://localhost:8501 |
