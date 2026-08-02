# Build Stage
FROM rust:1-alpine AS builder

WORKDIR /usr/src/app

RUN apk add --no-cache musl-dev pkgconfig openssl-dev

COPY src/validator/ .

RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/usr/src/app/target \
    cargo build --release && \
    cp target/release/validator /tmp/sentinel-validator

# Runtime Stage
FROM alpine:3.19

LABEL org.opencontainers.image.source="https://github.com/enesgulerdev/sentinel"

WORKDIR /app

RUN apk add --no-cache openssl ca-certificates && \
    addgroup -S sentinelgroup && \
    adduser -S -G sentinelgroup sentineluser

COPY --from=builder --chown=sentineluser:sentinelgroup /tmp/sentinel-validator ./sentinel-validator

USER sentineluser

CMD ["./sentinel-validator"]
