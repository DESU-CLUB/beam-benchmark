import os
import json
import subprocess
import pytest


MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/event_pipeline/app.py"
APP_NAME = "event-driven-pipeline"
VOLUME_NAME = "pipeline-artifacts"
DICT_NAME = "pipeline-registry"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Deploy the app and trigger a manual run before all tests."""
    deploy_result = modal_cli("deploy", APP_FILE, timeout=300)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )
    run_result = modal_cli("run", APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )
    yield
    modal_cli("app", "stop", APP_NAME)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"Expected app file {APP_FILE} does not exist."


def test_deploy_succeeds(deployed_app):
    """Deployment must succeed — this validates the code is correct Modal code."""
    pass  # Assertion is in the fixture


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a["Description"] for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list output: {app_names}"
    )


def test_volume_listed(deployed_app):
    result = modal_cli("volume", "list", "--json")
    assert result.returncode == 0, f"modal volume list failed: {result.stderr}"
    volumes = json.loads(result.stdout)
    volume_names = [v["Name"] for v in volumes]
    assert VOLUME_NAME in volume_names, (
        f"Volume '{VOLUME_NAME}' not found in modal volume list output: {volume_names}"
    )


def test_dict_total_processed(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "total_processed")
    assert result.returncode == 0, (
        f"Failed to get key 'total_processed' from Dict '{DICT_NAME}': {result.stderr}"
    )
    output = result.stdout.strip()
    assert "3" in output, (
        f"Expected 'total_processed' to contain '3' in Dict '{DICT_NAME}', got: {output!r}"
    )


def test_volume_has_files(deployed_app):
    result = modal_cli("volume", "ls", VOLUME_NAME)
    assert result.returncode == 0, f"modal volume ls {VOLUME_NAME} failed: {result.stderr}"
    output = result.stdout.strip()
    assert output != "", (
        f"Volume '{VOLUME_NAME}' appears to be empty — expected at least one result file."
    )


def test_app_file_has_retries():
    """Secondary verification: worker function must have retries=2."""
    with open(APP_FILE) as f:
        source = f.read()
    assert "retries=2" in source, (
        "Worker function must be configured with retries=2 in @app.function() decorator."
    )


def test_app_file_has_app_name():
    """Secondary verification: app must be named 'event-driven-pipeline'."""
    with open(APP_FILE) as f:
        source = f.read()
    assert "event-driven-pipeline" in source, (
        "App must be named 'event-driven-pipeline' in modal.App() call."
    )


def test_app_file_has_fastapi_app():
    """Secondary verification: must use @modal.fastapi_app() decorator."""
    with open(APP_FILE) as f:
        source = f.read()
    assert "fastapi_app" in source, (
        "App must use @modal.fastapi_app() decorator to expose the web API."
    )
