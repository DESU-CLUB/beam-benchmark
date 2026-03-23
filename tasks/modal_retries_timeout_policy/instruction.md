# Task: Configure Modal Function Retries and Timeout

Create a Modal app at `/home/user/modal_project/app.py` named `retry-demo`.

## Requirements

- Define `flaky_task` with `@app.function(retries=3, timeout=30)` that:
  - Tracks attempt count via a local file (defaulting to `/home/user/modal_project/attempts.txt`).
  - Raises `RuntimeError('simulated failure')` on the first two attempts.
  - Returns `{'success': True, 'attempts': count}` on the third attempt.
- Define a `@app.local_entrypoint()` named `main` that calls `flaky_task.remote()` and writes the result as JSON to `/home/user/modal_project/task_result.json`.

## Deployment

```
modal deploy /home/user/modal_project/app.py --env modal-vsdatagen
modal run /home/user/modal_project/app.py --env modal-vsdatagen
```

Verify `/home/user/modal_project/task_result.json` exists with `"success": true`.
