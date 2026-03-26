import os
import json
import subprocess
import pytest

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/hp_sweep/app.py"
APP_NAME = "hp-sweep-checkpoint"
VOLUME_NAME = "hp-sweep-results"
DICT_NAME = "hp-sweep-state"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Deploy the app, run it to populate Dict/Volume, then stop on teardown."""
    deploy_result = modal_cli("deploy", APP_FILE, timeout=300)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )
    run_result = modal_cli("run", APP_FILE, timeout=600)
    assert run_result.returncode == 0, (
        f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )
    yield
    modal_cli("app", "stop", APP_NAME)


def test_file_exists():
    assert os.path.isfile(APP_FILE), f"Expected app file {APP_FILE} does not exist."


def test_deploy_succeeds(deployed_app):
    """Deployment must succeed — validates that the code is correct Modal code."""
    pass  # Assertion is in the fixture


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a["Description"] for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list output: {app_names}"
    )


def test_volume_exists(deployed_app):
    result = modal_cli("volume", "list", "--json")
    assert result.returncode == 0, f"modal volume list failed: {result.stderr}"
    volumes = json.loads(result.stdout)
    volume_names = [v["Name"] for v in volumes]
    assert VOLUME_NAME in volume_names, (
        f"Volume '{VOLUME_NAME}' not found in modal volume list output: {volume_names}"
    )


def test_dict_has_items(deployed_app):
    result = modal_cli("dict", "items", DICT_NAME, "--json")
    assert result.returncode == 0, (
        f"Failed to list Dict items for '{DICT_NAME}':\n{result.stderr}"
    )
    items = json.loads(result.stdout)
    assert len(items) >= 2, (
        f"Expected at least 2 items in Dict '{DICT_NAME}' "
        f"('best_config' and 'best_score'), got {len(items)}: {items}"
    )
