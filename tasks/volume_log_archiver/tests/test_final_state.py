import json
import os
import subprocess
import pytest


MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_volume_logs/app.py"
APP_NAME = "volume-log-archiver"
VOLUME_NAME = "log-archive-vol"
DICT_NAME = "volume-log-archiver-output"


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
    deploy_result = modal_cli("deploy", "--env", MODAL_ENV, APP_FILE, timeout=300)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nSTDOUT: {deploy_result.stdout}\nSTDERR: {deploy_result.stderr}"
    )

    run_result = modal_cli("run", "--env", MODAL_ENV, APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"modal run failed:\nSTDOUT: {run_result.stdout}\nSTDERR: {run_result.stderr}"
    )

    yield {
        "deploy": deploy_result,
        "run": run_result,
    }

    modal_cli("app", "stop", APP_NAME, "--env", MODAL_ENV, timeout=60)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"App file {APP_FILE} does not exist"


def test_deploy_succeeds(deployed_app):
    assert deployed_app["deploy"].returncode == 0


def test_app_in_app_list(deployed_app):
    result = modal_cli("app", "list", "--json", "--env", MODAL_ENV, timeout=60)
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_descriptions = [a.get("Description", "") for a in apps]
    assert APP_NAME in app_descriptions, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_descriptions}"
    )


def test_volume_in_volume_list(deployed_app):
    result = modal_cli("volume", "list", "--json", "--env", MODAL_ENV, timeout=60)
    assert result.returncode == 0, f"modal volume list failed: {result.stderr}"
    volumes = json.loads(result.stdout)
    volume_names = [v.get("Name", "") for v in volumes]
    assert VOLUME_NAME in volume_names, (
        f"Volume '{VOLUME_NAME}' not found in modal volume list. Found: {volume_names}"
    )


def test_dict_log_count(deployed_app):
    result = modal_cli(
        "dict", "get", DICT_NAME, "log_count", "--env", MODAL_ENV, timeout=60
    )
    assert result.returncode == 0, (
        f"modal dict get log_count failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )
    value_str = result.stdout.strip()
    try:
        log_count = int(value_str)
    except ValueError:
        pytest.fail(f"log_count value is not an integer: '{value_str}'")
    assert log_count >= 3, f"log_count is {log_count}, expected >= 3"


def test_dict_log_content(deployed_app):
    result = modal_cli(
        "dict", "get", DICT_NAME, "log_content", "--env", MODAL_ENV, timeout=60
    )
    assert result.returncode == 0, (
        f"modal dict get log_content failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )
    log_content = result.stdout.strip()
    assert len(log_content) > 0, "log_content is empty"
    assert "\n" in log_content or len(log_content) > 10, (
        "log_content does not appear to contain log entries"
    )
