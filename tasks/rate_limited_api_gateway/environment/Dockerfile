FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-venv python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"
LABEL Description="Modal project with starter gateway.py stub in /home/user/modal_project for a stateful rate-limited API gateway task."

RUN mkdir -p /home/user/modal_project && \
    cat >/home/user/modal_project/gateway.py <<'EOF'
import modal

app = modal.App("rate-limited-gateway")
EOF

# Container contents:
#   - /home/user/modal_project  — Modal project directory with:
#       - gateway.py             (starter Modal App stub with empty App definition)
#   - Python 3, pip, pytest, and modal SDK available for automated verification.
#   - Task: Build a stateful rate-limited API gateway using Modal Class, Dict, Secret, and FastAPI web endpoint.

CMD ["/bin/bash"]
