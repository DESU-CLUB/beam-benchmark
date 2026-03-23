# Task: Parallel Text Summarizer Pipeline on Modal

Create a Modal app at `/home/user/modal_project/summarizer.py` named `text-summarizer` with two parallel functions.

## Requirements

- Build a custom image from `modal.Image.debian_slim()`.
- Define `summarize_text(text: str, max_words: int)` → `{'original_words': int, 'summary': str, 'truncated': bool}`.
- Define `compute_stats(summaries: list)` → `{'total': int, 'truncated_count': int, 'avg_original_words': float}`.
- Both use `@app.function(image=image)`.
- `@app.local_entrypoint()` named `main`:
  - Maps `summarize_text` over 4 sample texts with `max_words=3`.
  - Calls `compute_stats.remote(summaries)`.
  - Writes stats to `/home/user/modal_project/stats_output.json`.

## Deployment

```
modal deploy /home/user/modal_project/summarizer.py --env modal-vsdatagen
modal run /home/user/modal_project/summarizer.py --env modal-vsdatagen
```

Verify `stats_output.json` has `total=4`.
