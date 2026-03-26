FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-venv python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"
LABEL Description="Event-driven pipeline task with Modal Queue, Dict, Volume, FastAPI web endpoint, and retries at /home/user/event_pipeline."

RUN mkdir -p /home/user/event_pipeline && \
    cat >/home/user/event_pipeline/app.py <<'EOF'
import modal

app = modal.App("event-driven-pipeline")
EOF

# Container contents:
#   - /home/user/event_pipeline  — Modal project directory with:
#       - app.py  (starter Modal App stub named 'event-driven-pipeline')
#   - Python 3, pip, pytest, and modal SDK available for automated verification.

CMD ["/bin/bash"]
