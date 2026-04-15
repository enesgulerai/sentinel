# Stage 1: Builder
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install uv

# Create an isolated virtual environment for UI dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY docker/frontend/requirements.txt .
RUN uv pip install --no-cache -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Enforce the use of the virtual environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN groupadd -r sentinel && useradd -r -m -g sentinel sentinel

# Copy the isolated virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

COPY --chown=sentinel:sentinel src/ui/ ./src/ui/

USER sentinel

EXPOSE 8501

CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
