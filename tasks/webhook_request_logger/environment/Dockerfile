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

RUN pip3 install --break-system-packages modal requests

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"

RUN mkdir -p /home/user/modal_webhook

RUN printf 'import modal\n\napp = modal.App("webhook-logger")\n' > /home/user/modal_webhook/app.py

CMD ["/bin/bash"]
