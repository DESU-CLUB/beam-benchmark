import json
import os
import subprocess
import pytest


MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_pipeline/pipeline.py"
APP_NAME = "text-index-pipeline"
VOLUME_NAME = "text-index-volume"
DICT_NAME = "text-index-output"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Deploy and run the app before running tests."""
    deploy_result = modal_cli("deploy", APP_FILE)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )
    run_result = modal_cli("run", APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )
    yield
    modal_cli("app", "stop", APP_NAME)


def test_file_exists():
    assert os.path.isfile(APP_FILE), f"Expected pipeline.py at {APP_FILE} does not exist."


def test_deploy_succeeds(deployed_app):
    pass  # Assertion is in the fixture


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a["Description"] for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_volume_listed(deployed_app):
    result = modal_cli("volume", "list", "--json")
    assert result.returncode == 0, f"modal volume list failed: {result.stderr}"
    volumes = json.loads(result.stdout)
    volume_names = [v["Name"] for v in volumes]
    assert VOLUME_NAME in volume_names, (
        f"Volume '{VOLUME_NAME}' not found. Found: {volume_names}"
    )


def test_volume_has_index_files(deployed_app):
    result = modal_cli("volume", "ls", VOLUME_NAME, "/index")
    assert result.returncode == 0, (
        f"modal volume ls failed: {result.stderr}"
    )
    assert "doc_" in result.stdout, (
        f"No doc_*.txt files found in /index directory of volume. Output: {result.stdout}"
    )


def test_dict_doc_count(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "doc_count")
    assert result.returncode == 0, (
        f"Failed to get key 'doc_count' from Dict '{DICT_NAME}': {result.stderr}"
    )
    count_str = result.stdout.strip()
    try:
        count = int(count_str)
    except ValueError:
        pytest.fail(f"doc_count value is not an integer: '{count_str}'")
    assert count >= 3, f"doc_count should be >= 3, got {count}"
