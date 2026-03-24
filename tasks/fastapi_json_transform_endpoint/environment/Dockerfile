FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    git \
    python3 \
    python3-pip \
    python3-venv \
    python3-pytest \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal fastapi

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"

RUN mkdir -p /home/user/modal_fastapi && \
    printf 'import modal\n\napp = modal.App("fastapi-json-transform")\n' \
    > /home/user/modal_fastapi/app.py

CMD ["/bin/bash"]
