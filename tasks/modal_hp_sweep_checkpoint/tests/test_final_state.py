import os
import subprocess
import json
import re
import pytest

APP_NAME = "modal-hp-sweep-checkpoint"
APP_FILE = "/home/user/modal_project/modal_hp_sweep_checkpoint.py"
DICT_NAME = "modal-hp-sweep-checkpoint-output"
VOLUME_NAME = "modal-hp-sweep-checkpoint-vol"
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
    # Create the volume if it doesn't already exist
    vol_list = run_modal(["volume", "list", "--json"], timeout=60, check=False)
    volumes = json.loads(vol_list.stdout) if vol_list.stdout.strip() else []
    existing_volumes = [v.get("Name", "") for v in volumes]
    if VOLUME_NAME not in existing_volumes:
        run_modal(["volume", "create", VOLUME_NAME], timeout=60)

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


def test_volume_checkpoint_file_exists(deployed_app):
    result = run_modal(
        ["volume", "ls", VOLUME_NAME, "/"],
        timeout=60,
        check=False,
    )
    assert "best_params.json" in result.stdout, (
        f"File 'best_params.json' not found in volume. "
        f"Output: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_dict_best_lr(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "best_lr"], timeout=60)
    raw = result.stdout.strip()
    try:
        float(raw)
    except ValueError:
        pytest.fail(f"Dict key 'best_lr' is not a float. Got: '{raw}'")


def test_dict_best_batch_size(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "best_batch_size"], timeout=60)
    raw = result.stdout.strip()
    try:
        int(raw)
    except ValueError:
        pytest.fail(f"Dict key 'best_batch_size' is not an integer. Got: '{raw}'")


def test_dict_best_score(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "best_score"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = float(raw)
    except ValueError:
        pytest.fail(f"Dict key 'best_score' is not a float. Got: '{raw}'")
    assert value > 0.0, (
        f"Dict key 'best_score' must be > 0.0, got {value}"
    )


def test_dict_total_trials(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "total_trials"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"Dict key 'total_trials' is not an integer. Got: '{raw}'")
    assert value >= 4, (
        f"Dict key 'total_trials' must be >= 4, got {value}"
    )


def test_dict_checkpoint_path(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "checkpoint_path"], timeout=60)
    value = result.stdout.strip()
    assert value == "/checkpoints/best_params.json", (
        f"Dict key 'checkpoint_path' must equal '/checkpoints/best_params.json', got '{value}'"
    )
