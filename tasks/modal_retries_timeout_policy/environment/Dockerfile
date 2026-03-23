FROM ubuntu:24.04

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl ca-certificates git python3 python3-pip python3-venv python3-pytest bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal

RUN mkdir -p /home/user && chmod 0755 /home/user

LABEL Author="modal-task-builder"
LABEL Description="Modal retries and timeout policy task at /home/user/modal_project."

RUN mkdir -p /home/user/modal_project

CMD ["/bin/bash"]
