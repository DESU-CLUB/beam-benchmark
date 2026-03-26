import os
import json
import re
import subprocess
import pytest

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/embedding_service/app.py"
APP_NAME = "gpu-embedding-service"
DICT_NAME = "embedding-service-stats"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Deploy the app, invoke the endpoint, then yield for tests. Stop app on teardown."""
    # Deploy the app
    deploy_result = modal_cli("deploy", APP_FILE, timeout=600)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )

    # Extract web endpoint URL from deploy output
    deploy_output = deploy_result.stdout + deploy_result.stderr
    url_match = re.search(r"https://[^\s]+\.modal\.run[^\s]*", deploy_output)
    endpoint_url = url_match.group(0).rstrip(".") if url_match else None

    # Invoke the endpoint to populate the Modal Dict
    if endpoint_url:
        import urllib.request
        import urllib.error

        payload = json.dumps({"text": "hello world"}).encode("utf-8")
        req = urllib.request.Request(
            endpoint_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                pass  # Response consumed — dict should be populated
        except urllib.error.URLError:
            pass  # Continue tests even if invocation fails; dict check will catch missing data

    yield

    # Teardown: stop the app
    modal_cli("app", "stop", APP_NAME)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"App file {APP_FILE} does not exist."


def test_deploy_succeeds(deployed_app):
    """Deployment must succeed — validates the code is correct Modal code."""
    pass  # Assertion is in the fixture


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    try:
        apps = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"modal app list --json returned invalid JSON:\n{result.stdout}")
    app_names = [a.get("Description", "") for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_volume_listed(deployed_app):
    result = modal_cli("volume", "list", "--json")
    assert result.returncode == 0, f"modal volume list failed: {result.stderr}"
    try:
        volumes = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"modal volume list --json returned invalid JSON:\n{result.stdout}")
    assert len(volumes) > 0, (
        f"No volumes found in modal volume list. Expected at least one volume for model caching."
    )


def test_dict_has_entries(deployed_app):
    result = modal_cli("dict", "items", DICT_NAME, "--json")
    assert result.returncode == 0, (
        f"Failed to list items from Dict '{DICT_NAME}':\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    try:
        items = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"modal dict items --json returned invalid JSON:\n{result.stdout}")
    assert len(items) >= 2, (
        f"Dict '{DICT_NAME}' must have at least 2 entries (request count + token count). "
        f"Found {len(items)} entries: {items}"
    )
    # Verify values are non-zero (at least one request was made)
    values = [item.get("value", 0) if isinstance(item, dict) else item for item in items]
    assert any(v >= 1 for v in values if isinstance(v, (int, float))), (
        f"Dict '{DICT_NAME}' entries should have at least one value >= 1. Got: {items}"
    )
