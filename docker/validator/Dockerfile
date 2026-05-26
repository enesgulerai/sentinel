# STAGE 1: Builder
FROM rust:1-slim AS builder
WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y pkg-config libssl-dev

COPY src/validator/ .
RUN cargo build --release

# STAGE 2: Runtime
FROM debian:bookworm-slim
WORKDIR /app

RUN apt-get update && apt-get install -y libssl3 ca-certificates && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/src/app/target/release/validator ./sentinel-validator

CMD ["./sentinel-validator"]
