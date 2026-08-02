# Build Stage
FROM golang:1.26-alpine AS builder

WORKDIR /app

COPY src/api/go.mod src/api/go.sum ./

RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

COPY src/api/ .

RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o sentinel-api main.go

# Runtime Stage
FROM alpine:3.19

LABEL org.opencontainers.image.source="https://github.com/enesgulerdev/sentinel"

WORKDIR /app

RUN apk --no-cache add ca-certificates && \
    addgroup -S sentinelgroup && \
    adduser -S sentineluser -G sentinelgroup

COPY --from=builder /app/sentinel-api .

USER sentineluser

EXPOSE 8000

CMD ["./sentinel-api"]
