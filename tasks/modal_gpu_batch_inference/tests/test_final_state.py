import json
import os
import subprocess
import pytest

APP_FILE = "/home/user/modal_project/modal_gpu_batch_inference.py"
APP_NAME = "modal-gpu-batch-inference"
DICT_NAME = "modal-gpu-batch-inference-output"
VOLUME_NAME = "modal-gpu-batch-inference-vol"
SECRET_NAME = "modal-gpu-batch-inference-secret"
MODAL_ENV = "modal-vsdatagen"


@pytest.fixture(scope="module", autouse=True)
def deploy_and_run():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV

    # Create the secret
    subprocess.run(
        [
            "modal", "secret", "create", SECRET_NAME,
            "MODEL_NAME=linear-v1",
            "INFERENCE_BATCH_SIZE=16",
            "--force",
        ],
        env=env,
        timeout=120,
    )

    # Deploy the app
    deploy_result = subprocess.run(
        ["modal", "deploy", APP_FILE],
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )

    # Run the local entrypoint
    run_result = subprocess.run(
        ["modal", "run", APP_FILE],
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert run_result.returncode == 0, (
        f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )

    yield

    # Teardown: stop the app
    subprocess.run(
        ["modal", "app", "stop", APP_NAME],
        env=env,
        timeout=120,
    )


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"App file not found: {APP_FILE}"


def test_app_in_modal_app_list():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal", "app", "list", "--json"],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a.get("Description", "") for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_volume_exists():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal", "volume", "list", "--json"],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert result.returncode == 0, f"modal volume list failed: {result.stderr}"
    volumes = json.loads(result.stdout)
    volume_names = [v.get("Name", "") for v in volumes]
    assert VOLUME_NAME in volume_names, (
        f"Volume '{VOLUME_NAME}' not found. Found: {volume_names}"
    )


def test_secret_exists():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal", "secret", "list", "--json"],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert result.returncode == 0, f"modal secret list failed: {result.stderr}"
    secrets = json.loads(result.stdout)
    secret_names = [s.get("Name", "") for s in secrets]
    assert SECRET_NAME in secret_names, (
        f"Secret '{SECRET_NAME}' not found. Found: {secret_names}"
    )


def test_volume_contains_weights():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal", "volume", "ls", VOLUME_NAME, "/"],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )
    assert result.returncode == 0, (
        f"modal volume ls failed: {result.stderr}"
    )
    assert "weights.npy" in result.stdout, (
        f"weights.npy not found in volume. Output: {result.stdout}"
    )


def test_dict_model_name():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal", "dict", "get", DICT_NAME, "model_name"],
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert result.returncode == 0, f"modal dict get model_name failed: {result.stderr}"
    assert result.stdout.strip() == "linear-v1", (
        f"Expected model_name='linear-v1', got: '{result.stdout.strip()}'"
    )


def test_dict_total_samples():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal", "dict", "get", DICT_NAME, "total_samples"],
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert result.returncode == 0, f"modal dict get total_samples failed: {result.stderr}"
    assert result.stdout.strip() == "128", (
        f"Expected total_samples='128', got: '{result.stdout.strip()}'"
    )


def test_dict_batches_processed():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal", "dict", "get", DICT_NAME, "batches_processed"],
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert result.returncode == 0, f"modal dict get batches_processed failed: {result.stderr}"
    assert result.stdout.strip() == "8", (
        f"Expected batches_processed='8', got: '{result.stdout.strip()}'"
    )


def test_dict_avg_prediction_parseable_as_float():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal", "dict", "get", DICT_NAME, "avg_prediction"],
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert result.returncode == 0, f"modal dict get avg_prediction failed: {result.stderr}"
    value = result.stdout.strip()
    try:
        float(value)
    except ValueError:
        pytest.fail(f"avg_prediction is not parseable as float: '{value}'")


def test_dict_weights_path():
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal", "dict", "get", DICT_NAME, "weights_path"],
        capture_output=True,
        text=True,
        env=env,
        timeout=900,
    )
    assert result.returncode == 0, f"modal dict get weights_path failed: {result.stderr}"
    assert result.stdout.strip() == "/models/weights.npy", (
        f"Expected weights_path='/models/weights.npy', got: '{result.stdout.strip()}'"
    )
