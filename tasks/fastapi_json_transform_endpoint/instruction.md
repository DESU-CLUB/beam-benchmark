# Task: FastAPI JSON Transform Endpoint on Modal

You are building a serverless API layer using Modal. A starter file already exists at `/home/user/modal_fastapi/app.py` with a Modal app named `"fastapi-json-transform"`. Your job is to extend this file into a fully working FastAPI web endpoint that transforms JSON data.

## Requirements

### 1. Modal Image

Define a Modal image using `modal.Image.debian_slim()` with `fastapi` installed via `pip_install`.

### 2. FastAPI ASGI Endpoint

Create a FastAPI application inside a Modal function. The function must be decorated with both `@app.function()` (using the image you defined) and `@modal.asgi_app()`.

The FastAPI app must expose two routes:

- **`GET /`** — Returns a JSON response:
  ```json
  {"status": "ok", "service": "json-transform"}
  ```

- **`POST /transform`** — Accepts a JSON request body with two fields:
  - `data`: a list of values
  - `operation`: a string specifying the transformation

  Behavior:
  - If `operation` is `"reverse"`, return the list reversed.
  - If `operation` is `"sort"`, return the list sorted.
  - Otherwise, return the list unchanged.

  Example request body:
  ```json
  {"data": [3, 1, 2], "operation": "sort"}
  ```
  Expected response:
  ```json
  {"result": [1, 2, 3]}
  ```

### 3. Local Entrypoint

Add a `@app.local_entrypoint()` function that:
1. Calls the deployed endpoint to verify it is working (e.g., makes an HTTP request to the `GET /` route or checks the URL).
2. Stores results in a Modal Dict named `"fastapi-json-transform-output"` with:
   - Key `"health_check"` set to `"ok"`
   - Key `"endpoint_deployed"` set to `True`

## Deploying and Running

Deploy the app with:
```bash
modal deploy /home/user/modal_fastapi/app.py -e modal-vsdatagen
```

Then run the local entrypoint with:
```bash
modal run /home/user/modal_fastapi/app.py -e modal-vsdatagen
```
