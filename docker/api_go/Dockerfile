# Stage 1: Build the optimized Go binary
FROM golang:1.26-alpine AS builder

WORKDIR /app

# Copy go.mod and go.sum from the source directory
COPY src/api_go/go.mod src/api_go/go.sum ./
RUN go mod download

# Copy the actual Go source code
COPY src/api_go/ .

# Compile the binary with production optimizations
# CGO_ENABLED=0 removes C dependency for static linking
# -ldflags="-s -w" strips debug information and symbols to drastically minimize size
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o sentinel-api main.go

# Stage 2: Create the final ultra-lightweight runtime image
FROM alpine:3.19

WORKDIR /app

# Install ca-certificates for secure external network communications
RUN apk --no-cache add ca-certificates

# Copy only the compiled binary from the builder stage
COPY --from=builder /app/sentinel-api .

# Expose the Go API gateway port
EXPOSE 8081

# Execute the static binary
CMD ["./sentinel-api"]