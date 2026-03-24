import json
import os
import subprocess
import pytest


MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_class/app.py"
APP_NAME = "class-inference-warm"
DICT_NAME = "class-inference-output"


def modal_cli(*args, timeout=600):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Deploy and run the app before running tests."""
    deploy_result = modal_cli("deploy", APP_FILE, timeout=600)
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
    assert os.path.isfile(APP_FILE), f"Expected app.py at {APP_FILE} does not exist."


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


def test_dict_classifications_count(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "classifications")
    assert result.returncode == 0, (
        f"Failed to get key 'classifications' from Dict '{DICT_NAME}': {result.stderr}"
    )
    value = result.stdout.strip()
    assert value in ("3", 3) or int(value) == 3, (
        f"Expected classifications count of 3, got: '{value}'"
    )


def test_dict_stats_non_empty(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "stats")
    assert result.returncode == 0, (
        f"Failed to get key 'stats' from Dict '{DICT_NAME}': {result.stderr}"
    )
    stats_value = result.stdout.strip()
    assert len(stats_value) > 0, "stats value in Dict is empty"
    assert stats_value != "None", "stats value should not be None"


def test_source_has_enter_decorator(deployed_app):
    """Verify @modal.enter() decorator is present in the source file."""
    with open(APP_FILE) as f:
        source = f.read()
    assert "@modal.enter()" in source, (
        "Source does not contain @modal.enter() decorator"
    )


def test_source_has_method_decorator(deployed_app):
    """Verify @modal.method() decorator is present in the source file."""
    with open(APP_FILE) as f:
        source = f.read()
    assert "@modal.method()" in source, (
        "Source does not contain @modal.method() decorator"
    )


def test_source_has_min_containers(deployed_app):
    """Verify min_containers is set in the @app.cls decorator."""
    with open(APP_FILE) as f:
        source = f.read()
    assert "min_containers" in source, (
        "Source does not contain min_containers configuration for warm pool"
    )
