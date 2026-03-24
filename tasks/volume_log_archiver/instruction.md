# Volume Log Archiver

You are a DevOps engineer setting up a scheduled data job using the Modal serverless platform. Your goal is to build a Modal app that uses a Modal Volume for persistent shared storage to write and read log entries.

## What to Build

Edit the existing file at `/home/user/modal_volume_logs/app.py` to implement the following:

### Modal Volume

Create a Modal Volume named `"log-archive-vol"` and mount it at `/logs` in all functions that need it.

### Functions

1. **`write_logs`** — A Modal function that:
   - Writes 3 timestamped log entries to `/logs/archive.log` inside the volume
   - Returns the number of lines written as an integer

2. **`read_logs`** — A Modal function that:
   - Reads the contents of `/logs/archive.log` from the volume
   - Returns the file contents as a string

### Local Entrypoint

Add a `@app.local_entrypoint()` function that:
- Calls `write_logs` (using `.remote()`) and stores the returned line count
- Calls `read_logs` (using `.remote()`) and stores the returned content
- Saves results to a Modal Dict named `"volume-log-archiver-output"` with:
  - Key `"log_count"`: the integer count of lines written
  - Key `"log_content"`: the string contents of the log file

## Deploy and Run

Deploy the app:
```bash
modal deploy /home/user/modal_volume_logs/app.py -e modal-vsdatagen
```

Run the local entrypoint:
```bash
modal run /home/user/modal_volume_logs/app.py -e modal-vsdatagen
```
