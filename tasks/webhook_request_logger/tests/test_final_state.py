import json
import os
import subprocess
import pytest


MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_webhook/app.py"
APP_NAME = "webhook-logger"
DICT_NAME = "webhook-logger-output"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Deploy and run the app before running tests."""
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


def test_file_exists():
    assert os.path.isfile(APP_FILE), f"Expected app.py at {APP_FILE} does not exist."


def test_deploy_succeeds(deployed_app):
    pass  # Assertion is in the fixture


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a["Description"] for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_dict_last_message(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "last_message")
    assert result.returncode == 0, (
        f"Failed to get key 'last_message' from Dict '{DICT_NAME}': {result.stderr}"
    )
    value = result.stdout.strip()
    assert len(value) > 0, "last_message is empty"


def test_dict_call_count(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "call_count")
    assert result.returncode == 0, (
        f"Failed to get key 'call_count' from Dict '{DICT_NAME}': {result.stderr}"
    )
    raw = result.stdout.strip()
    assert len(raw) > 0, "call_count is empty"
    try:
        count = int(raw)
    except ValueError:
        pytest.fail(f"call_count is not an integer: '{raw}'")
    assert count >= 1, f"Expected call_count >= 1, got {count}"
