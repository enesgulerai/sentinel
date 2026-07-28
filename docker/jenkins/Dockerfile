# Stage 1: Downloader (Builder)
FROM alpine:3.19 AS builder

RUN apk add --no-cache curl tar
WORKDIR /downloads

# Download and extract the Docker binary
RUN curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-24.0.9.tgz -o docker.tgz && \
    tar xzvf docker.tgz

# Stage 2: Final Jenkins Image
FROM jenkins/jenkins:lts-alpine

USER root

# Copy ONLY the extracted docker binary from the builder stage
COPY --from=builder /downloads/docker/docker /usr/local/bin/docker

# Set executable permissions
RUN chmod +x /usr/local/bin/docker

# Drop privileges back to the jenkins user
USER jenkins
