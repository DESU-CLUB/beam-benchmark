#!/bin/bash
set -e

cat > /home/user/modal_cron/reporter.py << 'EOF'
import modal
from datetime import datetime, timezone

app = modal.App("status-reporter")

image = modal.Image.debian_slim().pip_install("requests")

@app.function(image=image, schedule=modal.Period(hours=6))
def report_status():
    timestamp = datetime.now(timezone.utc).isoformat()
    output_dict = modal.Dict.from_name("status-reporter-output", create_if_missing=True)
    output_dict.put("last_run", timestamp)
    output_dict.put("status", "success")
    return timestamp

@app.local_entrypoint()
def main():
    result = report_status.remote()
    print(f"Status reported at: {result}")
EOF

modal deploy /home/user/modal_cron/reporter.py -e modal-vsdatagen
modal run /home/user/modal_cron/reporter.py -e modal-vsdatagen
