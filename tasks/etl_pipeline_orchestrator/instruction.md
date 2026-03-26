# Fault-Tolerant ETL Pipeline on Modal

You are a platform engineer tasked with building a production-grade, fault-tolerant ETL pipeline using Modal's serverless infrastructure. The entire system must be implemented in a single file: `/home/user/modal_project/etl.py`.

## System Requirements

Build a Modal App named `etl-pipeline` that operates as an end-to-end data pipeline with the following capabilities:

### Data Ingestion (Scheduled)
The pipeline must automatically ingest synthetic data on a **5-minute schedule** using `modal.Period(minutes=5)`. The ingestion component generates batches of raw records (each with a category drawn from a small fixed set, a numeric value, and a timestamp), persists them as JSON files on a **Modal NetworkFileSystem (NFS)** named `etl-nfs`, and immediately kicks off data processing for the new batch. Each ingestion run must produce a distinct file using the naming convention `raw_<timestamp>.json`. Use `create_if_missing=True` when referencing the NFS.

### Data Processing (Fault-Tolerant)
A separate processing function reads a raw data file from the NFS, aggregates the records by category (computing statistics such as count and sum per category), and writes the aggregated output back to the NFS using the naming convention `processed_<timestamp>.json`. This function must be configured with **`retries=3` and `timeout=120`** to handle transient failures gracefully.

### Live Status Endpoint (FastAPI)
Expose a **GET `/status`** web endpoint using FastAPI that reads the most recently written processed results from the NFS and returns the pipeline statistics as JSON. If no processed data is available, the endpoint should return a JSON response clearly indicating the pipeline has not run yet. This endpoint must have access to the NFS.

### Pipeline Metadata (Modal Dict)
All pipeline run metadata must be persisted in a **Modal Dict named `etl-pipeline-metadata`** (use `create_if_missing=True`). The dict must track at minimum these exact keys:
- `run_count` — an integer counter that increments each ingestion cycle (must be >= 1 after a manual run)
- `last_run_timestamp` — the timestamp of the most recent successful run
- `error_count` — an integer counter for processing failures

### Manual Trigger
Implement a `@app.local_entrypoint()` that allows the pipeline to be triggered manually — running the full ingest-and-process cycle — so the system can be tested without waiting for the cron schedule to fire.

## Deployment Instructions

Set `MODAL_ENVIRONMENT=modal-vsdatagen` in your shell before running any Modal commands:

```
export MODAL_ENVIRONMENT=modal-vsdatagen
```

Deploy the app:

```
modal deploy /home/user/modal_project/etl.py
```

After deployment, trigger a manual run to populate the NFS and Dict:

```
modal run /home/user/modal_project/etl.py
```

**Do NOT use the `-e` CLI flag.** Always set `MODAL_ENVIRONMENT` as an environment variable instead.
