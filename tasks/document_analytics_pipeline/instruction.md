# Distributed Document Processing and Analytics Pipeline on Modal

You are a platform engineer building a distributed document processing and analytics pipeline on Modal. The entire system must be implemented in a single file: `/home/user/modal_project/pipeline.py`.

## System Requirements

Build a Modal App named `"document-analytics-pipeline"` with the following capabilities:

### Scheduled Ingestion (Cron)
The pipeline must run on an **hourly cron schedule**. Each run processes a corpus of synthetic text documents.

### Parallel Processing (Map/Starmap)
Process documents in parallel using Modal's `map` or `starmap`. For each document, perform NLP-style text analysis using **only Python's standard library**:
- `word_count` — total number of words in the document
- `sentence_count` — total number of sentences
- `keywords` — extracted keywords (e.g., most frequent words)
- `char_count` — total number of characters

### Pipeline Authentication (Modal Secret)
Use a **Modal Secret named `pipeline-credentials`** with key `PIPELINE_API_KEY=super-secret-pipeline-key` to validate the pipeline API key before processing.

### Results Storage (Modal Dict)
Use a **Modal Dict named `doc-analytics-output`** (with `create_if_missing=True`) to store all results. The Dict must contain:

**Per-document entries** (at least 10 documents): Each document should be stored as a separate key (e.g., `doc_0`, `doc_1`, ..., `doc_9`) with a JSON value containing:
- `word_count` — integer word count
- `sentence_count` — integer sentence count
- `keywords` — list of extracted keywords
- `char_count` — integer character count

**Summary entry**: A key named `summary` containing a JSON object with:
- `total_documents` — the total number of documents processed
- `total_words` — the sum of all word counts across documents
- `avg_words_per_doc` — average words per document
- `timestamp` — an ISO timestamp of when the pipeline ran

The Dict must contain at least **11 entries total** (10 documents + 1 summary).

### Manual Trigger (Local Entrypoint)
Implement a `@app.local_entrypoint()` that runs the full pipeline — processing at least 10 synthetic documents and storing results in the Dict.

## Deployment Instructions

Set `MODAL_ENVIRONMENT=modal-vsdatagen` in your shell before running any Modal commands:

```
export MODAL_ENVIRONMENT=modal-vsdatagen
```

Deploy the app:

```
modal deploy /home/user/modal_project/pipeline.py
```

After deployment, trigger a manual run to populate the output Dict:

```
modal run /home/user/modal_project/pipeline.py
```

**Do NOT use the `-e` CLI flag.** Always set `MODAL_ENVIRONMENT` as an environment variable instead.
