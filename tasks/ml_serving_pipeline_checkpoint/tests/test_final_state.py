import os
import json
import subprocess
import re
import pytest

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_project/app.py"
APP_NAME = "ml-serving-pipeline"
VOLUME_NAME = "model-checkpoints"
SECRET_NAME = "ml-serving-api-secret"
DICT_NAME = "ml-serving-pipeline-output"
API_KEY_VALUE = "supersecretkey"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


def _get_endpoint_url():
    """Extract the web endpoint URL from modal app logs or app list."""
    # Try to get URL from deploy output stored in fixture, fall back to app list
    result = modal_cli("app", "list", "--json")
    if result.returncode != 0:
        return None
    try:
        apps = json.loads(result.stdout)
        for app in apps:
            if app.get("Description") == APP_NAME:
                # URL may appear in URLs or similar field — we need to get it from function logs
                break
    except (json.JSONDecodeError, KeyError):
        pass
    return None


@pytest.fixture(scope="module")
def deployed_app():
    """Create secret, deploy the app, invoke endpoint, then yield for tests."""
    # Step 1: Create the Modal Secret required for authentication
    secret_result = modal_cli("secret", "create", SECRET_NAME, f"API_KEY={API_KEY_VALUE}", "--force")
    assert secret_result.returncode == 0, (
        f"Failed to create secret '{SECRET_NAME}':\nstdout: {secret_result.stdout}\nstderr: {secret_result.stderr}"
    )

    # Step 2: Deploy the app
    deploy_result = modal_cli("deploy", APP_FILE, timeout=600)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )

    # Step 3: Extract web endpoint URL from deploy output
    deploy_output = deploy_result.stdout + deploy_result.stderr
    url_match = re.search(r"https://[^\s]+\.modal\.run[^\s]*", deploy_output)
    endpoint_url = url_match.group(0).rstrip(".") if url_match else None

    # Step 4: Invoke the endpoint to populate the Modal Dict
    if endpoint_url:
        import urllib.request
        import urllib.error

        payload = json.dumps({"features": [6.0]}).encode("utf-8")
        req = urllib.request.Request(
            endpoint_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": API_KEY_VALUE,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                pass  # Response consumed — dict should be populated
        except urllib.error.URLError:
            pass  # Continue tests even if invocation fails; dict check will catch missing data
    else:
        # Fallback: try modal run to trigger the endpoint via local entrypoint if available
        pass

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
    volume_names = [v.get("Name", "") for v in volumes]
    assert VOLUME_NAME in volume_names, (
        f"Volume '{VOLUME_NAME}' not found in modal volume list. Found: {volume_names}"
    )


def test_secret_listed(deployed_app):
    result = modal_cli("secret", "list", "--json")
    assert result.returncode == 0, f"modal secret list failed: {result.stderr}"
    try:
        secrets = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"modal secret list --json returned invalid JSON:\n{result.stdout}")
    secret_names = [s.get("Name", "") for s in secrets]
    assert SECRET_NAME in secret_names, (
        f"Secret '{SECRET_NAME}' not found in modal secret list. Found: {secret_names}"
    )


def test_volume_has_model_checkpoint(deployed_app):
    result = modal_cli("volume", "ls", VOLUME_NAME, "/model-checkpoints")
    # Also try root path in case volume root is used
    if result.returncode != 0 or "model.pkl" not in result.stdout:
        result2 = modal_cli("volume", "ls", VOLUME_NAME)
        assert "model.pkl" in result.stdout or "model.pkl" in result2.stdout, (
            f"model.pkl not found in volume '{VOLUME_NAME}'.\n"
            f"ls /model-checkpoints output: {result.stdout}\n"
            f"ls / output: {result2.stdout}"
        )


def test_dict_request_count(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "request_count")
    assert result.returncode == 0, (
        f"Failed to get 'request_count' from Dict '{DICT_NAME}':\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    raw = result.stdout.strip()
    assert raw != "", f"'request_count' value is empty in Dict '{DICT_NAME}'."
    try:
        count = int(float(raw))
    except ValueError:
        pytest.fail(f"'request_count' is not a number: {raw!r}")
    assert count >= 1, f"Expected request_count >= 1, got: {count}"


def test_dict_last_prediction(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "last_prediction")
    assert result.returncode == 0, (
        f"Failed to get 'last_prediction' from Dict '{DICT_NAME}':\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    raw = result.stdout.strip()
    assert raw != "", f"'last_prediction' value is empty in Dict '{DICT_NAME}'."
    try:
        prediction = float(raw)
    except ValueError:
        pytest.fail(f"'last_prediction' is not a float: {raw!r}")
    # For input [6.0] with a model trained on [[1],[2],[3],[4],[5]] -> [2,4,6,8,10],
    # the expected prediction is approximately 12.0
    assert prediction != 0.0, f"'last_prediction' should be a non-zero float, got: {prediction}"
