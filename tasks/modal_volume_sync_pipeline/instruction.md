# Modal Volume Sync Pipeline

You are a data engineer building a batch processing pipeline on Modal's serverless cloud platform. Your task is to implement a persistent shared storage workflow using Modal Volumes.

## Project Setup

Your project directory is at `/home/user/volume_pipeline/`. A starter file `app.py` has already been partially set up with:
- A Modal App named `volume-sync-pipeline`
- A Volume stub referencing `data-pipeline-vol`

**Do not change the app name, volume name, or project directory.**

## What You Need to Build

Complete the implementation in `/home/user/volume_pipeline/app.py` by adding the following components:

### 1. Custom Container Image
Define a Modal image that installs `pandas`. This image will be used by both pipeline functions since they process tabular CSV data.

### 2. Volume Mount
Ensure the Modal Volume (`data-pipeline-vol`) is mounted inside the container at a consistent path (e.g., `/data`). Use `modal.Volume.from_name('data-pipeline-vol', create_if_missing=True)` so the volume is created automatically on first use.

### 3. `write_data` Function
Implement a Modal function named `write_data` that:
- Runs with the custom image and the volume mounted
- Creates a small tabular dataset using `pandas` (a DataFrame with a few rows and columns)
- Writes the DataFrame to a CSV file inside the mounted volume directory
- Calls `vol.commit()` after writing to ensure changes are persisted to the volume
- Prints a confirmation message upon completion

### 4. `read_data` Function
Implement a Modal function named `read_data` that:
- Runs with the same custom image and volume mounted
- Calls `vol.reload()` to pull the latest committed state from the volume
- Reads the CSV file from the mounted volume path using `pandas`
- Returns the CSV contents as a string

### 5. Local Entrypoint
Add a `@app.local_entrypoint()` function that:
- Calls `write_data.remote()` to trigger the write on Modal infrastructure
- Calls `read_data.remote()` and captures the returned string
- Prints the CSV string to standard output

## Deployment

Once your implementation is complete, deploy the app with:

```bash
modal deploy /home/user/volume_pipeline/app.py -e modal-vsdatagen
```

## Verification

After deploying, confirm that:
- The app `volume-sync-pipeline` is listed in `modal app list`
- The volume `data-pipeline-vol` is listed in `modal volume list`

**Important:** The function names `write_data` and `read_data`, the volume name `data-pipeline-vol`, and the app name `volume-sync-pipeline` must remain exactly as specified — they are required by the automated tests.
