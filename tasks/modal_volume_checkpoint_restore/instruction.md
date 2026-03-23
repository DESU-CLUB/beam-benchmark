# Task: Modal Checkpoint/Restore System with Volume

Build a checkpoint and restore system at `/home/user/modal_project/checkpointer.py` named `checkpoint-system`.

Use a Volume named `checkpoints`. Implement:
- `save_checkpoint(job_id, step, state)` — writes state JSON and updates a manifest file, commits volume.
- `restore_checkpoint(job_id, step=None)` — reads latest or specific checkpoint from volume.
- `list_checkpoints(job_id)` — returns the manifest dict.

Run two saves for job `job-001` (steps 1 and 2), restore latest, list checkpoints, and write `{'latest_state': ..., 'manifest': ...}` to `/home/user/modal_project/checkpoint_report.json`.

Deploy with `modal deploy /home/user/modal_project/checkpointer.py --env modal-vsdatagen` and run with `modal run`.

Verify app, volume, and `checkpoint_report.json` with `manifest.latest_step=2`.
