# Task: Multi-Entry Modal App with Shared Volume Orchestration

Build `/home/user/modal_project/orchestrator.py` named `multi-entry-app` with three pipeline stages — ingest, process, export — using a shared Volume named `shared-state`. A local entrypoint `main` runs all three in sequence and writes a report to `/home/user/modal_project/report.json`.

Deploy: `modal deploy /home/user/modal_project/orchestrator.py --env modal-vsdatagen`
Run: `modal run /home/user/modal_project/orchestrator.py --env modal-vsdatagen`

Verify `modal app list`, `modal volume list`, and `report.json` contains `ingest`, `process`, and `export` keys.
