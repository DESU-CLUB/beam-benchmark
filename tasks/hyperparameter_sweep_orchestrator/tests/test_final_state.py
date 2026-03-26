import os
import json
import subprocess
import pytest

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_project/sweep.py"
APP_NAME = "hyperparameter-sweep"
VOLUME_NAME = "hp-sweep-experiments"
DICT_NAME = "hp-sweep-results"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Deploy the app, run local_entrypoint to populate Dict/Volume, then clean up."""
    deploy_result = modal_cli("deploy", APP_FILE)
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
    """Deployment must succeed — validates the code is correct Modal code."""
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


def test_volume_has_experiment_files(deployed_app):
    result = modal_cli("volume", "ls", VOLUME_NAME)
    assert result.returncode == 0, f"modal volume ls failed: {result.stderr}"
    output = result.stdout
    assert len(output.strip()) > 0, (
        f"Volume '{VOLUME_NAME}' appears to be empty — expected experiment JSON files."
    )
    # Check that there is at least one .json file or file listing
    assert ".json" in output or len(output.strip().splitlines()) >= 1, (
        f"Expected JSON files in volume '{VOLUME_NAME}', got:\n{output}"
    )


def test_dict_best_config_exists(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "best_config")
    assert result.returncode == 0, (
        f"Failed to get 'best_config' from Dict '{DICT_NAME}':\n{result.stderr}"
    )
    output = result.stdout.strip()
    assert len(output) > 0, (
        f"'best_config' in Dict '{DICT_NAME}' is empty — expected a hyperparameter configuration."
    )
    # Should contain learning_rate or similar key indicating it's a hyperparameter config
    assert any(keyword in output.lower() for keyword in ["learning_rate", "lr", "batch_size", "bs"]), (
        f"'best_config' does not appear to contain hyperparameter data. Got: {output}"
    )


def test_dict_experiment_count_exists(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "experiment_count")
    assert result.returncode == 0, (
        f"Failed to get 'experiment_count' from Dict '{DICT_NAME}':\n{result.stderr}"
    )
    output = result.stdout.strip()
    assert len(output) > 0, (
        f"'experiment_count' in Dict '{DICT_NAME}' is empty — expected an integer."
    )
    try:
        count = int(output)
    except ValueError:
        raise AssertionError(
            f"'experiment_count' is not a valid integer. Got: {output!r}"
        )
    assert count >= 9, (
        f"Expected 'experiment_count' >= 9 (one per hyperparameter combination), got: {count}"
    )


def test_dict_items_present(deployed_app):
    result = modal_cli("dict", "items", DICT_NAME, "--json")
    assert result.returncode == 0, (
        f"Failed to list Dict items for '{DICT_NAME}':\n{result.stderr}"
    )
    items = json.loads(result.stdout)
    assert len(items) >= 2, (
        f"Expected at least 2 items in Dict '{DICT_NAME}' (best_config + experiment_count), got {len(items)}: {items}"
    )
