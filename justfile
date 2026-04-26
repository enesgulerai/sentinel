set shell := ["powershell.exe", "-c"]

# Displays this help menu listing all available commands
@default:
    just --list

# Downloads raw data and verifies integrity using SHA-256
fetch:
    uv run python -m src.data.ingestion

# Splits train/test sets and applies preprocessing without data leakage
preprocess: fetch
    uv run python -m src.features.preprocessing

# Trains tree-based models and benchmarks real-time inference latency
train: preprocess
    uv run python experiments/02_model_training.py

# Exports the champion XGBoost model to the universal ONNX format
export:
    uv run python experiments/03_train_and_export.py

# Runs the complete end-to-end machine learning pipeline
pipeline: fetch preprocess train export
    @echo "SUCCESS: Full Machine Learning Pipeline Completed!"

# Wipes all generated datasets, scaled files, and trained models
clean:
    rm -f data/raw/creditcard.csv
    rm -f data/processed/*.csv
    rm -f models/*.joblib
    rm -f models/*.onnx
    @echo "All generated data and models have been wiped clean."

# Docker: Builds images and starts infrastructure containers in the background
up:
    docker compose up --build -d

# Docker: Shows the current status of running containers
ps:
    docker compose ps
