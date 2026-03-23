# Task: Modal Class with keep_warm and Lifecycle State

Create a Modal app at `/home/user/modal_project/app.py` named `warm-pool-server`.

## Requirements

- Build a custom image from `modal.Image.debian_slim()`.
- Define class `WarmServer` with `@app.cls(image=image, keep_warm=1)`:
  - `@modal.enter()` method `setup`: initializes `self.data_store = {}` and `self.request_count = 0`.
  - `@modal.method()` `handle_request(key, value)`: stores key/value, increments request count, returns dict.
  - `@modal.method()` `get_stats()`: returns `{'total_requests': ..., 'stored_keys': [...]}`.
- `@app.local_entrypoint()` named `main` that calls `handle_request.remote` twice with `('name', 'Alice')` and `('role', 'engineer')`, then calls `get_stats.remote()` and writes to `/home/user/modal_project/server_stats.json`.

## Deployment

```
modal deploy /home/user/modal_project/app.py --env modal-vsdatagen
modal run /home/user/modal_project/app.py --env modal-vsdatagen
```

Verify `server_stats.json` has `total_requests >= 2` and `stored_keys` containing `name` and `role`.
