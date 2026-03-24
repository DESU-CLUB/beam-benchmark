import json
import os
import subprocess
import pytest


MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_cron/reporter.py"
APP_NAME = "status-reporter"
DICT_NAME = "status-reporter-output"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Deploy and run the app before running tests."""
    deploy_result = modal_cli("deploy", APP_FILE)
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
    assert os.path.isfile(APP_FILE), f"Expected reporter.py at {APP_FILE} does not exist."


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


def test_dict_status_success(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "status")
    assert result.returncode == 0, (
        f"Failed to get key 'status' from Dict '{DICT_NAME}': {result.stderr}"
    )
    assert result.stdout.strip() == "success", (
        f"Expected status 'success', got: '{result.stdout.strip()}'"
    )


def test_dict_last_run_timestamp(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "last_run")
    assert result.returncode == 0, (
        f"Failed to get key 'last_run' from Dict '{DICT_NAME}': {result.stderr}"
    )
    timestamp = result.stdout.strip()
    assert len(timestamp) > 0, "last_run timestamp is empty"
    # Should look like an ISO timestamp (contains T or - separators)
    assert "T" in timestamp or "-" in timestamp, (
        f"last_run value does not look like an ISO timestamp: '{timestamp}'"
    )


def test_schedule_decorator_in_file(deployed_app):
    """Verify the schedule decorator is present in the file."""
    with open(APP_FILE) as f:
        source = f.read()
    assert "modal.Period" in source or "modal.Cron" in source, (
        "No schedule (modal.Period or modal.Cron) found in reporter.py"
    )
