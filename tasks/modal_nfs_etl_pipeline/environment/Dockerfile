FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-pytest \
    curl \
    ca-certificates \
    git \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal

RUN mkdir -p /home/user/etl_pipeline

RUN echo 'import modal\n\napp = modal.App("nfs-etl-pipeline")' > /home/user/etl_pipeline/app.py

WORKDIR /home/user
