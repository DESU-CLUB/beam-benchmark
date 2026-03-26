FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-venv python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"
LABEL Description="Modal project with starter app.py stub in /home/user/doc_pipeline for document OCR pipeline task."

RUN mkdir -p /home/user/doc_pipeline && \
    cat >/home/user/doc_pipeline/app.py <<'EOF'
import modal

app = modal.App("doc-ocr-pipeline")
EOF

# Container contents:
#   - /home/user/doc_pipeline  — Modal project directory with:
#       - app.py  (starter Modal App stub with empty app definition)
#   - Python 3, pip, pytest, and modal SDK available for automated verification.
#   - The agent must implement: DocumentProcessor class with @enter lifecycle,
#     Modal Volume for result persistence, Modal Secret for config,
#     Modal Dict for job tracking, and batch .map() processing.

CMD ["/bin/bash"]
