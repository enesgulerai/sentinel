# Build Stage
FROM rust:1-slim AS builder

WORKDIR /usr/src/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends pkg-config libssl-dev && \
    rm -rf /var/lib/apt/lists/*

COPY src/validator/Cargo.toml src/validator/Cargo.lock ./
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

COPY src/validator/ .
RUN touch src/main.rs && \
    cargo build --release

# Runtime Stage
FROM debian:bookworm-slim

LABEL org.opencontainers.image.source="https://github.com/enesgulerdev/sentinel"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libssl3 ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd -r sentinelgroup && \
    useradd -r -g sentinelgroup sentineluser

COPY --from=builder --chown=sentineluser:sentinelgroup /usr/src/app/target/release/validator ./sentinel-validator

USER sentineluser

CMD ["./sentinel-validator"]
