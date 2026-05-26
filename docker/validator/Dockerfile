# STAGE 1: Builder
FROM rust:1-slim AS builder

WORKDIR /usr/src/app

COPY src/validator/ .

RUN cargo build --release

# STAGE 2: Runtime
FROM debian:bookworm-slim

RUN useradd -m -s /bin/bash sentinel_user
WORKDIR /app

COPY --from=builder /usr/src/app/target/release/validator /app/validator

RUN chown sentinel_user:sentinel_user /app/validator
USER sentinel_user

CMD ["./validator"]
