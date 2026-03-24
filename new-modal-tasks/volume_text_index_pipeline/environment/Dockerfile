FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal pytest

RUN mkdir -p /home/user/modal_pipeline

RUN echo "import modal\n\napp = modal.App('text-index-pipeline')\n" > /home/user/modal_pipeline/pipeline.py

WORKDIR /home/user/modal_pipeline

CMD ["/bin/bash"]
