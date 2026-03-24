import os
import subprocess
import pytest
import json
import re

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_batch/app.py"
APP_NAME = "batch-word-freq"
DICT_NAME = "batch-word-freq-output"


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
    deploy_result = modal_cli("deploy", APP_FILE, timeout=300)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )

    run_result = modal_cli("run", APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )

    yield {"deploy": deploy_result, "run": run_result}

    modal_cli("app", "stop", APP_NAME, timeout=60)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"{APP_FILE} does not exist"


def test_deploy_succeeds(deployed_app):
    assert deployed_app["deploy"].returncode == 0


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json", timeout=60)
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    descriptions = [a.get("Description", "") for a in apps]
    assert APP_NAME in descriptions, (
        f"App '{APP_NAME}' not found in modal app list. Found: {descriptions}"
    )


def test_dict_frequencies_key(deployed_app):
    result = modal_cli(
        "dict", "get", DICT_NAME, "frequencies", timeout=60
    )
    assert result.returncode == 0, (
        f"Failed to get 'frequencies' from dict '{DICT_NAME}':\n{result.stderr}"
    )
    value = json.loads(result.stdout)
    assert isinstance(value, dict), f"'frequencies' should be a dict, got: {type(value)}"
    assert len(value) > 0, "'frequencies' dict should be non-empty"


def test_dict_sentence_count_key(deployed_app):
    result = modal_cli(
        "dict", "get", DICT_NAME, "sentence_count", timeout=60
    )
    assert result.returncode == 0, (
        f"Failed to get 'sentence_count' from dict '{DICT_NAME}':\n{result.stderr}"
    )
    value = json.loads(result.stdout)
    assert isinstance(value, int), f"'sentence_count' should be an int, got: {type(value)}"
    assert value >= 3, f"'sentence_count' should be >= 3, got: {value}"
