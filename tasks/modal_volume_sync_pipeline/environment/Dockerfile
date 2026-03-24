FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages modal pytest pandas

RUN mkdir -p /home/user/volume_pipeline

RUN cat > /home/user/volume_pipeline/app.py << 'EOF'
import modal

app = modal.App('volume-sync-pipeline')
vol = modal.Volume.from_name('data-pipeline-vol', create_if_missing=True)
EOF

WORKDIR /home/user/volume_pipeline
