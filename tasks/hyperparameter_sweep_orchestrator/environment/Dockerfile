FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-venv python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal numpy

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"
LABEL Description="Modal project with starter sweep.py (empty App stub) in /home/user/modal_project for hyperparameter sweep orchestration task."

RUN mkdir -p /home/user/modal_project && \
    cat >/home/user/modal_project/sweep.py <<'EOF'
import modal

app = modal.App("hyperparameter-sweep")
EOF

# Container contents:
#   - /home/user/modal_project  — Modal project directory with:
#       - sweep.py              (starter Modal App stub named "hyperparameter-sweep")
#   - Python 3, pip, pytest, modal SDK, and numpy available system-wide.
#   - numpy pre-installed for synthetic training simulation in experiments.

CMD ["/bin/bash"]
