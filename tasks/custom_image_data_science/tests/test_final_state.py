import json
import os
import subprocess
import pytest


MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_ds/app.py"
APP_NAME = "custom-image-data-science"
DICT_NAME = "custom-image-ds-output"


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
    run_result = modal_cli("run", APP_FILE, timeout=600)
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


def test_dict_stats_nonempty(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "stats")
    assert result.returncode == 0, (
        f"Failed to get key 'stats' from Dict '{DICT_NAME}': {result.stderr}"
    )
    stats_str = result.stdout.strip()
    assert len(stats_str) > 0, "stats value is empty"
    assert stats_str != "None", "stats value is None"


def test_dict_packages_verified(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "packages_verified")
    assert result.returncode == 0, (
        f"Failed to get key 'packages_verified' from Dict '{DICT_NAME}': {result.stderr}"
    )
    value_str = result.stdout.strip()
    assert value_str.lower() in ("true", "1", "yes"), (
        f"packages_verified should indicate True, got: '{value_str}'"
    )


def test_image_has_pip_installs():
    with open(APP_FILE, "r") as f:
        source = f.read()
    assert "numpy" in source, "app.py does not reference 'numpy' in image pip_install"
    assert "pandas" in source, "app.py does not reference 'pandas' in image pip_install"
    assert "scipy" in source, "app.py does not reference 'scipy' in image pip_install"
