import os
import subprocess
import json
import pytest

APP_NAME = "hyperparameter-sweep-orchestrator"
APP_FILE = "/home/user/modal_project/hyperparameter_sweep_orchestrator.py"
DICT_NAME = "hyperparameter-sweep-orchestrator-output"
VOLUME_NAME = "hyperparameter-sweep-orchestrator-vol"
SECRET_NAME = "hyperparameter-sweep-orchestrator-secret"
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
    # Create the Modal Secret before deploying
    run_modal(
        [
            "secret", "create", SECRET_NAME,
            "EXPERIMENT_ID=sweep-run-001",
            "MAX_TRIALS=9",
            "--force",
        ],
        timeout=60,
    )

    # Deploy the app
    run_modal(
        ["deploy", APP_FILE],
        timeout=600,
    )

    # Run the local entrypoint to populate Dict and Volume
    run_modal(
        ["run", APP_FILE],
        timeout=600,
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


def test_volume_all_trials_file_exists(deployed_app):
    result = run_modal(
        ["volume", "ls", VOLUME_NAME, "/"],
        timeout=60,
        check=False,
    )
    assert "all_trials.json" in result.stdout, (
        f"File 'all_trials.json' not found in volume. "
        f"Output: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_volume_best_params_file_exists(deployed_app):
    result = run_modal(
        ["volume", "ls", VOLUME_NAME, "/"],
        timeout=60,
        check=False,
    )
    assert "best_params.json" in result.stdout, (
        f"File 'best_params.json' not found in volume. "
        f"Output: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_dict_experiment_id(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "experiment_id"], timeout=60)
    value = result.stdout.strip()
    assert value == "sweep-run-001", (
        f"Dict key 'experiment_id' must equal 'sweep-run-001', got '{value}'"
    )


def test_dict_total_trials(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "total_trials"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"Dict key 'total_trials' is not an integer. Got: '{raw}'")
    assert value >= 9, (
        f"Dict key 'total_trials' must be >= 9, got {value}"
    )


def test_dict_best_loss(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "best_loss"], timeout=60)
    raw = result.stdout.strip()
    try:
        float(raw)
    except ValueError:
        pytest.fail(f"Dict key 'best_loss' is not parseable as float. Got: '{raw}'")


def test_dict_best_lr(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "best_lr"], timeout=60)
    raw = result.stdout.strip()
    try:
        float(raw)
    except ValueError:
        pytest.fail(f"Dict key 'best_lr' is not parseable as float. Got: '{raw}'")


def test_dict_best_dropout(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "best_dropout"], timeout=60)
    raw = result.stdout.strip()
    try:
        float(raw)
    except ValueError:
        pytest.fail(f"Dict key 'best_dropout' is not parseable as float. Got: '{raw}'")
