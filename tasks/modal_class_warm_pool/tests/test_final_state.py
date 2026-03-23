import os
import json
import subprocess
import pytest

ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_project/app.py"
APP_NAME = "warm-pool-server"
STATS_FILE = "/home/user/modal_project/server_stats.json"

def modal_cli(*args, timeout=300):
    env = {**os.environ, "MODAL_ENVIRONMENT": ENV}
    cmd = ["modal"] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)

@pytest.fixture(scope="module")
def deployed_and_run():
    result = modal_cli("deploy", APP_FILE)
    assert result.returncode == 0, f"modal deploy failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    run_result = modal_cli("run", APP_FILE)
    assert run_result.returncode == 0, f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    yield
    modal_cli("app", "stop", APP_NAME)

def test_file_exists():
    assert os.path.isfile(APP_FILE), f"Expected app file {APP_FILE} does not exist."

def test_deploy_succeeds(deployed_and_run):
    pass

def test_app_listed(deployed_and_run):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_descriptions = [a.get("Description", a.get("description", a.get("name", ""))) for a in apps]
    assert any(APP_NAME in d for d in app_descriptions), f"App '{APP_NAME}' not found in: {app_descriptions}"

def test_stats_file_exists(deployed_and_run):
    assert os.path.isfile(STATS_FILE), f"server_stats.json not found at {STATS_FILE}."

def test_total_requests(deployed_and_run):
    with open(STATS_FILE) as f:
        data = json.load(f)
    assert data.get("total_requests", 0) >= 2, f"Expected total_requests >= 2, got: {data}"

def test_stored_keys(deployed_and_run):
    with open(STATS_FILE) as f:
        data = json.load(f)
    keys = data.get("stored_keys", [])
    assert "name" in keys, f"'name' not in stored_keys: {keys}"
    assert "role" in keys, f"'role' not in stored_keys: {keys}"
