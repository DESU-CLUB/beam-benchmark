import os
import json
import re
import subprocess
import pytest


MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_project/etl.py"
APP_NAME = "etl-pipeline"
NFS_NAME = "etl-nfs"
DICT_NAME = "etl-pipeline-metadata"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Deploy the app and trigger a manual run before all tests."""
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


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"Expected app file {APP_FILE} does not exist."


def test_deploy_succeeds(deployed_app):
    """Deployment must succeed — this validates the code is correct Modal code."""
    pass  # Assertion is in the fixture


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a["Description"] for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list output: {app_names}"
    )


def test_nfs_listed(deployed_app):
    result = modal_cli("nfs", "list", "--json")
    assert result.returncode == 0, f"modal nfs list failed: {result.stderr}"
    nfs_list = json.loads(result.stdout)
    nfs_names = [n["Name"] for n in nfs_list]
    assert NFS_NAME in nfs_names, (
        f"NFS '{NFS_NAME}' not found in modal nfs list output: {nfs_names}"
    )


def test_dict_run_count(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "run_count")
    assert result.returncode == 0, (
        f"Failed to get key 'run_count' from Dict '{DICT_NAME}': {result.stderr}"
    )
    raw = result.stdout.strip()
    assert raw != "", f"'run_count' value is empty in Dict '{DICT_NAME}'"
    # Accept integer values >= 1 (may be returned as string or int representation)
    try:
        count = int(float(raw))
    except ValueError:
        pytest.fail(f"'run_count' is not a numeric value: {raw!r}")
    assert count >= 1, (
        f"Expected run_count >= 1 in '{DICT_NAME}', got: {count}"
    )


def test_dict_last_run_timestamp(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "last_run_timestamp")
    assert result.returncode == 0, (
        f"Failed to get key 'last_run_timestamp' from Dict '{DICT_NAME}': {result.stderr}"
    )
    value = result.stdout.strip()
    assert value != "", (
        f"'last_run_timestamp' is empty in Dict '{DICT_NAME}'"
    )


def test_nfs_has_raw_files(deployed_app):
    result = modal_cli("nfs", "ls", NFS_NAME)
    assert result.returncode == 0, f"modal nfs ls {NFS_NAME} failed: {result.stderr}"
    output = result.stdout
    # Check for at least one raw_*.json file
    assert re.search(r"raw_\S+\.json", output), (
        f"No raw_*.json files found in NFS '{NFS_NAME}':\n{output}"
    )


def test_nfs_has_processed_files(deployed_app):
    result = modal_cli("nfs", "ls", NFS_NAME)
    assert result.returncode == 0, f"modal nfs ls {NFS_NAME} failed: {result.stderr}"
    output = result.stdout
    # Check for at least one processed_*.json file
    assert re.search(r"processed_\S+\.json", output), (
        f"No processed_*.json files found in NFS '{NFS_NAME}':\n{output}"
    )


def test_etl_file_has_retries_and_timeout():
    """Secondary verification: processing function must have retries=3 and timeout=120."""
    with open(APP_FILE) as f:
        source = f.read()
    assert "retries=3" in source, (
        "Processing function must be configured with retries=3 in @app.function decorator."
    )
    assert "timeout=120" in source, (
        "Processing function must be configured with timeout=120 in @app.function decorator."
    )


def test_etl_file_has_cron_schedule():
    """Secondary verification: cron function must use Period(minutes=5) schedule."""
    with open(APP_FILE) as f:
        source = f.read()
    assert re.search(r"Period\s*\(\s*minutes\s*=\s*5\s*\)", source), (
        "Cron function must use modal.Period(minutes=5) schedule."
    )


def test_etl_file_app_name():
    """Secondary verification: app must be named 'etl-pipeline'."""
    with open(APP_FILE) as f:
        source = f.read()
    assert "etl-pipeline" in source, (
        "App must be named 'etl-pipeline' in modal.App() call."
    )
