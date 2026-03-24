FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

LABEL Author="modal-task-builder"

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

RUN mkdir -p /home/user/modal_class

RUN printf 'import modal\n\napp = modal.App("class-inference-warm")\n' > /home/user/modal_class/app.py

CMD ["/bin/bash"]
