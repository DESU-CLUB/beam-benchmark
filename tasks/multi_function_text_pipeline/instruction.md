# Task: Build a Modal Text Processing Pipeline

You have a starter Modal app at `/home/user/modal_pipeline/app.py` with app name `"text-pipeline"`. Your job is to extend it into a 3-function text processing pipeline.

## Requirements

### Image

Define a Modal image using `modal.Image.debian_slim()` and assign it to a variable (e.g. `image`).

### Functions

Implement three Modal functions, each decorated with `@app.function(image=image)`:

1. **`clean_text(text: str) -> str`**
   - Strips leading and trailing whitespace from the input
   - Converts the text to lowercase
   - Returns the cleaned string

2. **`count_words(text: str) -> int`**
   - Counts the number of words in the given text
   - Returns the count as an integer

3. **`summarize(original_text: str, word_count: int) -> dict`**
   - Returns a dictionary with the following keys:
     - `"original_length"`: the length of the original (uncleaned) text
     - `"word_count"`: the word count passed in
     - `"cleaned_length"`: the length of the cleaned version of the original text

### Local Entrypoint

Add a `@app.local_entrypoint()` function that:

1. Uses the sample text: `"  Hello World this is a TEST of the pipeline  "`
2. Calls `clean_text.remote()` on the sample text to get the cleaned version
3. Calls `count_words.remote()` on the cleaned text to get the word count
4. Calls `summarize.remote()` with the original text and the word count to get a summary dict
5. Stores results in a Modal Dict named `"text-pipeline-output"`:
   - Key `"summary"` = the dict returned by `summarize.remote()`
   - Key `"pipeline_stages"` = `3`

## Deploy and Run

Deploy the app:
```bash
modal deploy /home/user/modal_pipeline/app.py -e modal-vsdatagen
```

Then run the local entrypoint:
```bash
modal run /home/user/modal_pipeline/app.py -e modal-vsdatagen
```
