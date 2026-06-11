# Stage 1: Builder
FROM golang:1.26-alpine AS builder

WORKDIR /app

COPY src/api/go.mod src/api/go.sum ./
RUN go mod download

COPY src/api/ .

RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o sentinel-api main.go

# Stage 2: Runtime
FROM alpine:3.19

LABEL org.opencontainers.image.source="https://github.com/enesgulerdev/sentinel"

WORKDIR /app

RUN apk --no-cache add ca-certificates

COPY --from=builder /app/sentinel-api .

EXPOSE 8000

CMD ["./sentinel-api"]
