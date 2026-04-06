# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

RUN pip install uv

COPY docker/frontend/requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN groupadd -r sentinel && useradd -r -m -g sentinel sentinel

COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

COPY --chown=sentinel:sentinel src/ui/ ./src/ui/

USER sentinel

EXPOSE 8501

CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
