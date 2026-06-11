# Stage 1: Builder
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uv

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY docker/consumer/requirements.txt .
RUN uv pip install --no-cache -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/enesgulerdev/sentinel"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN groupadd -r sentinel && useradd -r -g sentinel sentinel
RUN mkdir -p /app/logs && chown -R sentinel:sentinel /app/logs

COPY --from=builder /opt/venv /opt/venv

COPY --chown=sentinel:sentinel src/ ./src/
COPY --chown=sentinel:sentinel models/ ./models/

USER sentinel

CMD ["python", "-m", "src.consumer.main"]
