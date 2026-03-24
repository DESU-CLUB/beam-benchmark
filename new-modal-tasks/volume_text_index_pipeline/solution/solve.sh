#!/bin/bash
set -e

# Write the complete pipeline.py solution
cat > /home/user/modal_pipeline/pipeline.py << 'EOF'
import modal
import os

app = modal.App("text-index-pipeline")

volume = modal.Volume.from_name("text-index-volume", environment_name="modal-vsdatagen")


@app.function(volumes={"/data": volume})
def index_documents(documents: list[str]) -> int:
    """Index documents by writing each to a separate file in /data/index/."""
    index_dir = "/data/index"
    os.makedirs(index_dir, exist_ok=True)

    for i, doc in enumerate(documents):
        file_path = f"{index_dir}/doc_{i}.txt"
        with open(file_path, "w") as f:
            f.write(doc)

    volume.commit()
    return len(documents)


@app.local_entrypoint()
def main():
    documents = ["hello world", "modal rocks", "data pipeline"]
    count = index_documents.remote(documents)
    print(f"Indexed {count} documents")

    output_dict = modal.Dict.from_name("text-index-output", create_if_missing=True)
    output_dict.put("doc_count", count)
EOF

# Deploy the app
modal deploy /home/user/modal_pipeline/pipeline.py -e modal-vsdatagen

# Run the pipeline
modal run /home/user/modal_pipeline/pipeline.py -e modal-vsdatagen
