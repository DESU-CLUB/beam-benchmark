import os
import subprocess
import json
import pytest

APP_NAME = "ml-serving-pipeline-checkpoint"
APP_FILE = "/home/user/modal_project/ml_serving_pipeline_checkpoint.py"
DICT_NAME = "ml-serving-pipeline-checkpoint-output"
VOLUME_NAME = "ml-serving-pipeline-checkpoint-vol"
SECRET_NAME = "ml-serving-pipeline-checkpoint-secret"
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
            "MODEL_VERSION=v1.0.0",
            "AUTH_TOKEN=serving-auth-abc123",
            "--force",
        ],
        timeout=60,
        check=False,
    )

    # Deploy the app
    run_modal(
        ["deploy", APP_FILE],
        timeout=600,
    )

    # Run the local entrypoint to populate the Dict and Volume
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


def test_volume_listed(deployed_app):
    result = run_modal(["volume", "list", "--json"], timeout=60)
    volumes = json.loads(result.stdout)
    vol_names = [v.get("Name", "") for v in volumes]
    assert VOLUME_NAME in vol_names, (
        f"Volume '{VOLUME_NAME}' not found in modal volume list. Found: {vol_names}"
    )


def test_secret_listed(deployed_app):
    result = run_modal(["secret", "list", "--json"], timeout=60)
    secrets = json.loads(result.stdout)
    secret_names = [s.get("Name", "") for s in secrets]
    assert SECRET_NAME in secret_names, (
        f"Secret '{SECRET_NAME}' not found in modal secret list. Found: {secret_names}"
    )


def test_volume_checkpoint_file_exists(deployed_app):
    result = run_modal(
        ["volume", "ls", VOLUME_NAME, "/"],
        timeout=60,
        check=False,
    )
    assert "model.npy" in result.stdout, (
        f"File 'model.npy' not found in volume. "
        f"Output: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_dict_model_version(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "model_version"], timeout=60)
    value = result.stdout.strip()
    assert value == "v1.0.0", (
        f"Dict key 'model_version' must equal 'v1.0.0', got '{value}'"
    )


def test_dict_checkpoint_saved(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "checkpoint_saved"], timeout=60)
    value = result.stdout.strip()
    assert value == "true", (
        f"Dict key 'checkpoint_saved' must equal 'true', got '{value}'"
    )


def test_dict_endpoint_ready(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "endpoint_ready"], timeout=60)
    value = result.stdout.strip()
    assert value == "true", (
        f"Dict key 'endpoint_ready' must equal 'true', got '{value}'"
    )


def test_dict_warm_pool_size(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "warm_pool_size"], timeout=60)
    value = result.stdout.strip()
    assert value == "2", (
        f"Dict key 'warm_pool_size' must equal '2', got '{value}'"
    )
