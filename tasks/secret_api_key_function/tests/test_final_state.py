import json
import os
import subprocess

import pytest

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_secrets/app.py"
APP_NAME = "secret-api-key"
SECRET_NAME = "my-api-credentials"
DICT_NAME = "secret-api-key-output"


def modal_cli(*args, timeout=300):
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal"] + list(args),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return result


@pytest.fixture(scope="module")
def deployed_app():
    # Create the secret first
    secret_result = modal_cli(
        "secret", "create", SECRET_NAME, "API_KEY=test-key-1234", "--force"
    )
    assert secret_result.returncode == 0, (
        f"Failed to create secret: {secret_result.stderr}"
    )

    # Deploy the app
    deploy_result = modal_cli("deploy", APP_FILE)
    assert deploy_result.returncode == 0, (
        f"Failed to deploy app: {deploy_result.stderr}"
    )

    # Run the app
    run_result = modal_cli("run", APP_FILE)
    assert run_result.returncode == 0, (
        f"Failed to run app: {run_result.stderr}"
    )

    yield {
        "deploy_result": deploy_result,
        "run_result": run_result,
    }

    # Teardown: stop the app
    modal_cli("app", "stop", APP_NAME)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"App file {APP_FILE} does not exist"


def test_deploy_succeeds(deployed_app):
    assert deployed_app["deploy_result"].returncode == 0, (
        f"Deploy failed: {deployed_app['deploy_result'].stderr}"
    )


def test_app_in_app_list(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a.get("Description", a.get("Name", a.get("name", ""))) for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_secret_in_secret_list(deployed_app):
    result = modal_cli("secret", "list", "--json")
    assert result.returncode == 0, f"modal secret list failed: {result.stderr}"
    secrets = json.loads(result.stdout)
    secret_names = [s.get("Name", s.get("name", "")) for s in secrets]
    assert SECRET_NAME in secret_names, (
        f"Secret '{SECRET_NAME}' not found in modal secret list. Found: {secret_names}"
    )


def test_dict_has_masked_key(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "masked_key")
    assert result.returncode == 0, (
        f"Failed to get masked_key from dict: {result.stderr}"
    )
    value = result.stdout.strip()
    assert len(value) > 0, "masked_key in dict is empty"
    assert len(value) == 4, (
        f"masked_key should be 4 characters, got {len(value)}: '{value}'"
    )


def test_dict_has_verified_true(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "verified")
    assert result.returncode == 0, (
        f"Failed to get verified from dict: {result.stderr}"
    )
    value = result.stdout.strip()
    assert value in ("True", "true", True), (
        f"verified in dict should be True, got: '{value}'"
    )
