# Task: Modal NetworkFileSystem Shared Storage

Create a Modal app at `/home/user/modal_project/app.py` named `nfs-demo` that uses a NetworkFileSystem (NFS) to share files between two functions.

## Requirements

- Create an NFS named `shared-fs` using `modal.NetworkFileSystem.from_name('shared-fs', create_if_missing=True)`.
- Define `write_shared_file` with `@app.function(network_file_systems={'/shared': nfs})` that writes `'hello from nfs'` to `/shared/message.txt`.
- Define `read_shared_file` with `@app.function(network_file_systems={'/shared': nfs})` that reads and returns the contents of `/shared/message.txt`.
- Define a `@app.local_entrypoint()` named `main` that calls write then read and writes the result to `/home/user/modal_project/nfs_output.txt`.

## Deployment

```
modal deploy /home/user/modal_project/app.py --env modal-vsdatagen
modal run /home/user/modal_project/app.py --env modal-vsdatagen
```

Verify `/home/user/modal_project/nfs_output.txt` exists and contains `hello from nfs`.
