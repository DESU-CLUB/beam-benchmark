import os
import json
import subprocess
import pytest

ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_project/benchmark.py"
APP_NAME = "gpu-benchmark"
RESULTS_FILE = "/home/user/modal_project/benchmark_results.json"

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

def test_results_file_exists(deployed_and_run):
    assert os.path.isfile(RESULTS_FILE), f"benchmark_results.json not found at {RESULTS_FILE}."

def test_total_runs(deployed_and_run):
    with open(RESULTS_FILE) as f:
        data = json.load(f)
    assert data.get("total_runs") == 3, f"Expected total_runs=3, got: {data.get('total_runs')}"

def test_devices_used(deployed_and_run):
    with open(RESULTS_FILE) as f:
        data = json.load(f)
    assert "devices_used" in data, f"'devices_used' missing: {data}"
    assert isinstance(data["devices_used"], list), f"devices_used must be a list"

def test_all_benchmarks(deployed_and_run):
    with open(RESULTS_FILE) as f:
        data = json.load(f)
    benchmarks = data.get("all_benchmarks", [])
    assert len(benchmarks) == 3, f"Expected 3 benchmarks, got: {len(benchmarks)}"
    assert all("matrix_multiply" in b for b in benchmarks), f"Benchmark names unexpected: {benchmarks}"
