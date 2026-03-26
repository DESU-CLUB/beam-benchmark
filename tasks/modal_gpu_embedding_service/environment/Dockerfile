FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-venv python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"
LABEL Description="Modal GPU embedding service environment with modal SDK and starter app.py in /home/user/embedding_service."

RUN mkdir -p /home/user/embedding_service && \
    cat >/home/user/embedding_service/app.py <<'EOF'
import modal

app = modal.App("gpu-embedding-service")
EOF

# Container contents:
#   - /home/user/embedding_service      — Modal project directory with:
#       - app.py                        (starter Modal App stub with empty App definition)
#   - Python 3, pip, pytest, modal SDK installed for evaluation.
#   - Agent must install sentence-transformers via Modal image in the app code.

CMD ["/bin/bash"]
