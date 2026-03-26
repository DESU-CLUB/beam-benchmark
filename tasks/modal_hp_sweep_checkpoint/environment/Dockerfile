FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3 python3-pip python3-venv python3-pytest curl ca-certificates git bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"
LABEL Description="Modal environment with starter app.py stub in /home/user/hp_sweep for hp-sweep-checkpoint task."

RUN mkdir -p /home/user/hp_sweep && \
    cat >/home/user/hp_sweep/app.py <<'EOF'
import modal

app = modal.App("hp-sweep-checkpoint")
EOF

# Container contents:
#   - /home/user/hp_sweep       — project directory with:
#       - app.py                (starter Modal App stub named "hp-sweep-checkpoint")
#   - Python 3, pip, pytest, and modal SDK available system-wide.

CMD ["/bin/bash"]
