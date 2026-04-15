# Stage 1: Builder
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uv

# Create an isolated virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY docker/backend/requirements.txt .
RUN uv pip install --no-cache -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Enforce the use of the virtual environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN groupadd -r sentinel && useradd -r -g sentinel sentinel

RUN mkdir -p /app/logs && chown -R sentinel:sentinel /app/logs

# Copy the completely isolated virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy all source code and essential ML artifacts
COPY --chown=sentinel:sentinel src/ ./src/
COPY --chown=sentinel:sentinel models/ ./models/

USER sentinel

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
