# Serverless ETL Pipeline with Network File System on Modal

You are a platform engineer building a serverless ETL pipeline on Modal that uses a Network File System as a shared staging area. The entire system must be implemented in a single file: `/home/user/etl_pipeline/app.py`.

## System Requirements

Build a Modal App named `"nfs-etl-pipeline"` with the following capabilities:

### ETL Processor (Modal Class with Lifecycle Hooks)
Define a stateful `ETLProcessor` class with lifecycle hooks that handles the extract-transform-load workflow.

### Shared Staging Area (Modal NFS)
Use a **Modal NetworkFileSystem named `etl-shared-fs`** (with `create_if_missing=True`) as the shared staging area for data between pipeline stages.

### Database Credentials (Modal Secret)
Use a **Modal Secret named `etl-db-config`** containing database credentials. The secret will be created with keys `DB_HOST` and `DB_PORT`. Your code should reference these keys from the secret (do NOT require any additional keys like `DB_USER` or `DB_PASSWORD` — only `DB_HOST` and `DB_PORT` are provided).

### Pipeline State Tracking (Modal Dict)
Use a **Modal Dict named `etl-pipeline-state`** (with `create_if_missing=True`) to track pipeline run status across batches. The Dict must contain:
- `last_run_status` — a string that includes `"success"` when the pipeline completes successfully
- `batches_processed` — the number of data batches processed (must be `2` after a full run)

### Cron-Scheduled Trigger
Include a cron-scheduled function that triggers the pipeline on a regular interval.

### Manual Trigger (Local Entrypoint)
Implement a `@app.local_entrypoint()` that processes **two data batches** and records the outcome in the shared Dict, setting `last_run_status` to include `"success"` and `batches_processed` to `2`.

## Deployment Instructions

Set `MODAL_ENVIRONMENT=modal-vsdatagen` in your shell before running any Modal commands:

```
export MODAL_ENVIRONMENT=modal-vsdatagen
```

Deploy the app:

```
MODAL_ENVIRONMENT=modal-vsdatagen modal deploy /home/user/etl_pipeline/app.py
```

After deployment, trigger a manual run to populate the NFS and Dict:

```
MODAL_ENVIRONMENT=modal-vsdatagen modal run /home/user/etl_pipeline/app.py
```

**Do NOT use the `-e` CLI flag.** Always set `MODAL_ENVIRONMENT` as an environment variable instead.
