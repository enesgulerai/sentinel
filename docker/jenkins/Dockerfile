FROM jenkins/jenkins:lts

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://download.docker.com/linux/static/stable/x86_64/docker-24.0.9.tgz -o docker.tgz && \
    tar xzvf docker.tgz && \
    mv docker/docker /usr/local/bin/ && \
    chmod +x /usr/local/bin/docker && \
    rm -rf docker docker.tgz && \
    rm -rf /var/lib/apt/lists/*
