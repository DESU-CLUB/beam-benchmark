import os
import json
import subprocess
import pytest

ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_project/summarizer.py"
APP_NAME = "text-summarizer"
STATS_FILE = "/home/user/modal_project/stats_output.json"

def modal_cli(*args, timeout=600):
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
    assert os.path.isfile(STATS_FILE), f"stats_output.json not found at {STATS_FILE}."

def test_stats_total(deployed_and_run):
    with open(STATS_FILE) as f:
        data = json.load(f)
    assert data.get("total") == 4, f"Expected total=4, got: {data.get('total')}"

def test_stats_truncated_count(deployed_and_run):
    with open(STATS_FILE) as f:
        data = json.load(f)
    assert "truncated_count" in data, f"'truncated_count' missing from stats: {data}"

def test_stats_avg_words(deployed_and_run):
    with open(STATS_FILE) as f:
        data = json.load(f)
    assert "avg_original_words" in data, f"'avg_original_words' missing from stats: {data}"
