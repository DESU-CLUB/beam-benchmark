import os
import subprocess
import pytest
import json
import re


MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_project/gateway.py"
APP_NAME = "rate-limited-gateway"
SECRET_NAME = "gateway-config"
DICT_NAME = "gateway-stats"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Create secret, deploy the app, run local entrypoint to populate Dict, then clean up."""
    # Create the gateway-config secret before deploying
    secret_result = modal_cli(
        "secret", "create", SECRET_NAME,
        "RATE_LIMIT_PER_MINUTE=10",
        "GATEWAY_API_KEY=test-secret-key",
        "--force",
    )
    assert secret_result.returncode == 0, (
        f"Failed to create secret '{SECRET_NAME}':\n"
        f"stdout: {secret_result.stdout}\nstderr: {secret_result.stderr}"
    )

    # Deploy the app
    deploy_result = modal_cli("deploy", APP_FILE, timeout=600)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )

    # Run the local entrypoint to populate the gateway-stats Dict
    run_result = modal_cli("run", APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )

    yield

    modal_cli("app", "stop", APP_NAME)


def test_gateway_file_exists():
    assert os.path.isfile(APP_FILE), (
        f"Expected gateway file {APP_FILE} does not exist."
    )


def test_deploy_succeeds(deployed_app):
    """Deployment must succeed — validated by the fixture."""
    pass  # Assertion is in the fixture


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a["Description"] for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list output: {app_names}"
    )


def test_secret_exists(deployed_app):
    result = modal_cli("secret", "list", "--json")
    assert result.returncode == 0, f"modal secret list failed: {result.stderr}"
    secrets = json.loads(result.stdout)
    secret_names = [s["Name"] for s in secrets]
    assert SECRET_NAME in secret_names, (
        f"Secret '{SECRET_NAME}' not found in modal secret list output: {secret_names}"
    )


def test_dict_total_requests(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "total_requests")
    assert result.returncode == 0, (
        f"Failed to get key 'total_requests' from Dict '{DICT_NAME}': {result.stderr}"
    )
    raw = result.stdout.strip()
    assert raw, f"'total_requests' key in Dict '{DICT_NAME}' is empty."
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"'total_requests' value is not an integer: '{raw}'")
    assert value >= 1, (
        f"Expected 'total_requests' >= 1 in Dict '{DICT_NAME}', got {value}"
    )


def test_dict_active_clients(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "active_clients")
    assert result.returncode == 0, (
        f"Failed to get key 'active_clients' from Dict '{DICT_NAME}': {result.stderr}"
    )
    raw = result.stdout.strip()
    assert raw, f"'active_clients' key in Dict '{DICT_NAME}' is empty."
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"'active_clients' value is not an integer: '{raw}'")
    assert value >= 1, (
        f"Expected 'active_clients' >= 1 in Dict '{DICT_NAME}', got {value}"
    )


def test_dict_rate_limited_count(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "rate_limited_count")
    assert result.returncode == 0, (
        f"Failed to get key 'rate_limited_count' from Dict '{DICT_NAME}': {result.stderr}"
    )
    raw = result.stdout.strip()
    assert raw, f"'rate_limited_count' key in Dict '{DICT_NAME}' is empty."
    try:
        int(raw)
    except ValueError:
        pytest.fail(f"'rate_limited_count' value is not an integer: '{raw}'")


def test_dict_has_all_stat_keys(deployed_app):
    result = modal_cli("dict", "items", DICT_NAME, "--json")
    assert result.returncode == 0, (
        f"Failed to list items in Dict '{DICT_NAME}': {result.stderr}"
    )
    items = json.loads(result.stdout)
    assert len(items) > 0, f"Dict '{DICT_NAME}' is empty — no stats were stored."
    # Extract keys from items (list of [key, value] pairs or dicts)
    if items and isinstance(items[0], list):
        keys = [item[0] for item in items]
    elif items and isinstance(items[0], dict):
        keys = [item.get("key", item.get("Key", "")) for item in items]
    else:
        keys = list(items.keys()) if isinstance(items, dict) else []

    required_keys = {"total_requests", "rate_limited_count", "active_clients"}
    missing = required_keys - set(keys)
    assert not missing, (
        f"Dict '{DICT_NAME}' is missing required stat keys: {missing}. "
        f"Found keys: {keys}"
    )
