import os
import json
import subprocess
import pytest

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/doc_pipeline/app.py"
APP_NAME = "doc-ocr-pipeline"
VOLUME_NAME = "ocr-output-volume"
SECRET_NAME = "ocr-api-config"
DICT_NAME = "ocr-job-tracker"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Create secret, deploy the app, run local entrypoint to populate volume and dict, then clean up."""
    # Create the OCR config secret before deploying
    secret_result = modal_cli(
        "secret", "create", SECRET_NAME,
        "PROCESSING_MODE=batch",
        "--force"
    )
    assert secret_result.returncode == 0, (
        f"Failed to create Modal secret '{SECRET_NAME}':\n"
        f"stdout: {secret_result.stdout}\nstderr: {secret_result.stderr}"
    )

    # Deploy the app
    deploy_result = modal_cli("deploy", APP_FILE, timeout=300)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )

    # Run local entrypoint to process documents and populate volume + dict
    run_result = modal_cli("run", APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )

    yield

    modal_cli("app", "stop", APP_NAME)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), (
        f"Expected app file {APP_FILE} does not exist."
    )


def test_deploy_succeeds(deployed_app):
    """Deployment must succeed — validated in the fixture."""
    pass


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list --json failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a["Description"] for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_volume_exists(deployed_app):
    result = modal_cli("volume", "list", "--json")
    assert result.returncode == 0, f"modal volume list --json failed: {result.stderr}"
    volumes = json.loads(result.stdout)
    volume_names = [v["Name"] for v in volumes]
    assert VOLUME_NAME in volume_names, (
        f"Volume '{VOLUME_NAME}' not found in modal volume list. Found: {volume_names}"
    )


def test_secret_exists(deployed_app):
    result = modal_cli("secret", "list", "--json")
    assert result.returncode == 0, f"modal secret list --json failed: {result.stderr}"
    secrets = json.loads(result.stdout)
    secret_names = [s["Name"] for s in secrets]
    assert SECRET_NAME in secret_names, (
        f"Secret '{SECRET_NAME}' not found in modal secret list. Found: {secret_names}"
    )


def test_dict_has_items(deployed_app):
    result = modal_cli("dict", "items", DICT_NAME, "--json")
    assert result.returncode == 0, (
        f"Failed to list Dict '{DICT_NAME}' items:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    items = json.loads(result.stdout)
    assert len(items) > 0, (
        f"Dict '{DICT_NAME}' is empty — expected at least 1 item after processing."
    )


def test_dict_total_processed(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "total_processed")
    assert result.returncode == 0, (
        f"Failed to get key 'total_processed' from Dict '{DICT_NAME}':\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    raw = result.stdout.strip()
    assert raw != "", (
        f"Dict '{DICT_NAME}' key 'total_processed' returned empty output."
    )
    # Accept either int or string representation — value must be >= 3
    try:
        value = int(raw)
    except ValueError:
        # Try to extract an integer from the output (e.g., "3\n" or "total_processed: 3")
        import re
        match = re.search(r"\d+", raw)
        assert match is not None, (
            f"Could not parse integer from 'total_processed' output: {raw!r}"
        )
        value = int(match.group())
    assert value >= 3, (
        f"Dict '{DICT_NAME}' key 'total_processed' is {value}, expected >= 3."
    )
