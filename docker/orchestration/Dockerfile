# Stage 1: Runtime
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Non-root user for security
RUN groupadd -r prefect && useradd -r -m -g prefect prefect

# Install uv for blazing fast dependency resolution
RUN pip install --no-cache-dir uv

# Install Dependencies
RUN uv pip install --no-cache --system prefect pandas numpy requests xgboost onnxmltools

# Copy the orchestration code
COPY --chown=prefect:prefect orchestration/ ./orchestration/

USER prefect

# The entrypoint runs our flow script, which connects to the Prefect server
CMD ["python", "orchestration/master_deploy.py"]
