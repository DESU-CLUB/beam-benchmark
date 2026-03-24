# Modal Webhook Processor

You are a backend developer migrating an existing HTTP webhook service to [Modal](https://modal.com), a serverless cloud platform. Your task is to implement a webhook processor using Modal that receives POST requests with JSON payloads and returns processed JSON responses.

## Project Location

Your project is located at `/home/user/webhook_processor/`. A starter file `app.py` already exists there with a basic Modal import and an empty App definition. Build on this file to complete the implementation.

## What to Build

Implement a Modal application that processes incoming webhook events. The application should:

1. **Use a Custom Image** — Define a Modal image that extends the default Python image with at least one additional pip package to support data validation.

2. **Expose a Webhook Endpoint** — Create a Modal function that:
   - Listens for `POST` requests
   - Accepts a JSON body containing an `event_type` field (string) and a `payload` field (dict)
   - Processes the incoming data and returns a JSON response that includes the original fields plus metadata indicating the event was received and processed

3. **Include a Local Entrypoint** — Add a `@app.local_entrypoint()` function so the webhook logic can be exercised locally before deployment.

## Requirements

- The file must remain at `/home/user/webhook_processor/app.py`
- The Modal App must keep the name `webhook-processor`
- The web endpoint function must be named `process_webhook`
- The local entrypoint function must be named `main`
- Deploy using: `modal deploy app.py -e modal-vsdatagen` from the `/home/user/webhook_processor/` directory

## Hints

- Use `@modal.web_endpoint(method="POST")` to expose an HTTP POST endpoint
- Modal integrates with FastAPI/Pydantic — you can define a `pydantic.BaseModel` subclass as the function parameter type and Modal will automatically parse the incoming JSON body
- The `@app.function(image=<your_image>)` decorator applies the custom image to your endpoint
- Use `modal.Image.debian_slim().pip_install(...)` to define a custom image

## Deployment

Once your implementation is ready, deploy the app from the project directory:

```bash
cd /home/user/webhook_processor
modal deploy app.py -e modal-vsdatagen
```

After a successful deployment, verify the app appears in:

```bash
modal app list -e modal-vsdatagen
```
