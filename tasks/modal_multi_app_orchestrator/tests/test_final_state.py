import os
import json
import subprocess
import pytest

ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_project/orchestrator.py"
APP_NAME = "multi-entry-app"
VOLUME_NAME = "shared-state"
REPORT_FILE = "/home/user/modal_project/report.json"

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

def test_volume_listed(deployed_and_run):
    result = modal_cli("volume", "list")
    assert result.returncode == 0, f"modal volume list failed: {result.stderr}"
    assert VOLUME_NAME in result.stdout, f"Volume '{VOLUME_NAME}' not found:\n{result.stdout}"

def test_report_file_exists(deployed_and_run):
    assert os.path.isfile(REPORT_FILE), f"report.json not found at {REPORT_FILE}."

def test_report_has_ingest(deployed_and_run):
    with open(REPORT_FILE) as f:
        data = json.load(f)
    assert "ingest" in data, f"'ingest' key missing from report.json: {data}"

def test_report_has_process(deployed_and_run):
    with open(REPORT_FILE) as f:
        data = json.load(f)
    assert "process" in data, f"'process' key missing from report.json: {data}"

def test_report_has_export(deployed_and_run):
    with open(REPORT_FILE) as f:
        data = json.load(f)
    assert "export" in data, f"'export' key missing from report.json: {data}"
