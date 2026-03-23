# Task: Modal Scheduled Data Snapshot with Volume

Create a Modal app at `/home/user/modal_project/snapshot.py` named `data-snapshot`.

## Requirements

- Create a Volume named `snapshot-store`.
- Define `take_snapshot` scheduled with `modal.Period(minutes=10)` and `volumes={'/snapshots': snapshot_volume}` that appends a JSON snapshot line to `/snapshots/snapshots.jsonl` and commits the volume.
- Define `get_snapshot_count` with `volumes={'/snapshots': snapshot_volume}` that reads `/snapshots/snapshots.jsonl` and returns the line count.
- Define `@app.local_entrypoint()` named `main` that calls `take_snapshot.remote()` once, then `get_snapshot_count.remote()`, and writes `{'snapshots': count}` to `/home/user/modal_project/snapshot_count.json`.

## Deployment

```
modal deploy /home/user/modal_project/snapshot.py --env modal-vsdatagen
modal run /home/user/modal_project/snapshot.py --env modal-vsdatagen
```

Verify `modal app list`, `modal volume list`, and `snapshot_count.json` shows at least 1 snapshot.
