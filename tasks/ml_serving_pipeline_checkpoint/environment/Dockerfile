FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-venv python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal scikit-learn

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"
LABEL Description="Modal ML serving pipeline environment with scikit-learn, modal SDK, and starter app.py in /home/user/modal_project."

RUN mkdir -p /home/user/modal_project && \
    cat >/home/user/modal_project/app.py <<'EOF'
import modal

app = modal.App("ml-serving-pipeline")
EOF

# Container contents:
#   - /home/user/modal_project       — Modal project directory with:
#       - app.py                     (starter Modal App stub with empty App definition)
#   - Python 3, pip, pytest, modal SDK, and scikit-learn installed for evaluation.
#   - scikit-learn available for model training inside Modal containers.

CMD ["/bin/bash"]
