Build a document OCR processing pipeline in `/home/user/doc_pipeline/app.py` that processes a batch of text documents in parallel on Modal, simulates OCR by extracting word count and character statistics from each document's text content, persists results as JSON files in a Modal Volume named `ocr-output-volume`, validates a processing configuration from a Modal Secret named `ocr-api-config` (which must contain `PROCESSING_MODE=batch`), and tracks job state — including a `total_processed` count — in a Modal Dict named `ocr-job-tracker`.

Your implementation must combine the following four Modal capabilities:

1. **Modal Class with lifecycle hook** — Define a class that initializes its processing context at container startup (before handling any documents), and exposes a method for processing individual documents. The class must have access to the volume and the secret.

2. **Modal Volume** (`ocr-output-volume`) — Persist each document's OCR result (word count, character count, document ID) as a JSON file inside the volume. Create the volume with `create_if_missing=True`.

3. **Modal Secret** (`ocr-api-config`) — Create this secret before deploying with `PROCESSING_MODE=batch`. The processing method must read and validate `PROCESSING_MODE` from the environment; if it is missing or not equal to `batch`, raise an error.

4. **Modal Dict** (`ocr-job-tracker`) — Track processing state across the batch. At minimum, store a `total_processed` key containing the integer count of documents processed (must be >= 3). Create the dict with `create_if_missing=True`.

The `local_entrypoint` must drive the full pipeline: define at least 3 sample text documents as strings in your code, fan them out for parallel processing using `.map()` or `.starmap()`, write results to the volume, and update the dict with the total count.

The Modal App must be named `doc-ocr-pipeline`.

Set `MODAL_ENVIRONMENT=modal-vsdatagen` and deploy using:
```
modal deploy /home/user/doc_pipeline/app.py
```

After deploying, trigger the pipeline with:
```
MODAL_ENVIRONMENT=modal-vsdatagen modal run /home/user/doc_pipeline/app.py
```
