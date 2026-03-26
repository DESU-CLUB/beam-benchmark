FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-venv python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"
LABEL Description="Modal project with starter pipeline.py stub in /home/user/modal_project for distributed document analytics pipeline task."

RUN mkdir -p /home/user/modal_project && \
    cat >/home/user/modal_project/pipeline.py <<'EOF'
import modal

app = modal.App("document-analytics-pipeline")
EOF

# Container contents:
#   - /home/user/modal_project  — Modal project directory with:
#       - pipeline.py  (starter Modal App stub with empty app definition)
#   - Python 3, pip, pytest, and modal SDK available for automated verification.
#   - The agent must implement: cron scheduling, parallel .map()/.starmap() processing,
#     Modal Dict storage, and Modal Secret validation.

CMD ["/bin/bash"]
