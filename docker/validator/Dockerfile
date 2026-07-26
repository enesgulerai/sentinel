# Build Stage
FROM rust:1-alpine AS builder

WORKDIR /usr/src/app

RUN apk add --no-cache musl-dev pkgconfig openssl-dev

COPY src/validator/Cargo.toml src/validator/Cargo.lock ./
RUN mkdir src && \
    echo "fn main() {}" > src/main.rs && \
    cargo build --release && \
    rm -rf src

COPY src/validator/ .
RUN touch src/main.rs && \
    cargo build --release

# Runtime Stage
FROM alpine:3.19

LABEL org.opencontainers.image.source="https://github.com/enesgulerdev/sentinel"

WORKDIR /app

RUN apk add --no-cache openssl ca-certificates && \
    addgroup -S sentinelgroup && \
    adduser -S -G sentinelgroup sentineluser

COPY --from=builder --chown=sentineluser:sentinelgroup /usr/src/app/target/release/validator ./sentinel-validator

USER sentineluser

CMD ["./sentinel-validator"]
