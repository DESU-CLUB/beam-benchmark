FROM ubuntu:24.04

LABEL Author="modal-task-builder"

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

RUN pip3 install --break-system-packages modal

RUN mkdir -p /home/user && chmod 0755 /home/user

RUN mkdir -p /home/user/modal_batch

RUN printf 'import modal\n\napp = modal.App("batch-word-freq")\n' > /home/user/modal_batch/app.py

CMD ["/bin/bash"]
