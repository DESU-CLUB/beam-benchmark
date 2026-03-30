import os
import subprocess
import json
import pytest

APP_NAME = "rate-limited-api-gateway"
APP_FILE = "/home/user/modal_project/rate_limited_api_gateway.py"
DICT_NAME = "rate-limited-api-gateway-output"
SECRET_NAME = "rate-limited-api-gateway-secret"
MODAL_ENV = os.environ.get("MODAL_ENVIRONMENT", "modal-vsdatagen")


def run_modal(args, timeout=300, check=True):
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal"] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"modal {' '.join(args)} failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
    return result


@pytest.fixture(scope="module")
def deployed_app():
    # Create the secret
    run_modal(
        [
            "secret", "create", SECRET_NAME,
            "GATEWAY_API_KEY=gateway-key-prod-2024",
            "RATE_LIMIT_MAX=100",
            "--force",
        ],
        timeout=60,
    )

    # Deploy the app
    run_modal(
        ["deploy", APP_FILE],
        timeout=600,
    )

    # Run the local entrypoint to populate the Dict
    run_modal(
        ["run", APP_FILE],
        timeout=300,
    )

    yield

    # Teardown: stop the app
    run_modal(["app", "stop", APP_NAME], timeout=60, check=False)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"App file {APP_FILE} does not exist"


def test_deploy_succeeds(deployed_app):
    # If the fixture completed without raising, deploy succeeded
    pass


def test_app_listed(deployed_app):
    result = run_modal(["app", "list", "--json"], timeout=60)
    apps = json.loads(result.stdout)
    app_names = [a.get("Description", "") for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_secret_listed(deployed_app):
    result = run_modal(["secret", "list", "--json"], timeout=60)
    secrets = json.loads(result.stdout)
    secret_names = [s.get("Name", "") for s in secrets]
    assert SECRET_NAME in secret_names, (
        f"Secret '{SECRET_NAME}' not found in modal secret list. Found: {secret_names}"
    )


def test_dict_total_requests_processed(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "total_requests_processed"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"Dict key 'total_requests_processed' is not an integer. Got: '{raw}'")
    assert value > 0, (
        f"Dict key 'total_requests_processed' must be > 0, got {value}"
    )


def test_dict_rate_limit_hits(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "rate_limit_hits"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"Dict key 'rate_limit_hits' is not an integer. Got: '{raw}'")
    assert value >= 0, (
        f"Dict key 'rate_limit_hits' must be >= 0, got {value}"
    )


def test_dict_gateway_status(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "gateway_status"], timeout=60)
    value = result.stdout.strip()
    assert value == "operational", (
        f"Dict key 'gateway_status' must equal 'operational', got '{value}'"
    )


def test_dict_api_version(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "api_version"], timeout=60)
    value = result.stdout.strip()
    assert value == "v1", (
        f"Dict key 'api_version' must equal 'v1', got '{value}'"
    )
