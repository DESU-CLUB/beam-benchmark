import json
import os
import subprocess

import pytest

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_fastapi/app.py"
APP_NAME = "fastapi-json-transform"
DICT_NAME = "fastapi-json-transform-output"


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
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )

    run_result = modal_cli("run", "--env", MODAL_ENV, APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )

    yield {
        "deploy_stdout": deploy_result.stdout,
        "deploy_stderr": deploy_result.stderr,
        "run_stdout": run_result.stdout,
        "run_stderr": run_result.stderr,
    }

    modal_cli("app", "stop", APP_NAME, "--env", MODAL_ENV, timeout=60)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"App file {APP_FILE} does not exist"


def test_deploy_succeeds(deployed_app):
    assert deployed_app is not None


def test_app_in_app_list(deployed_app):
    result = modal_cli("app", "list", "--json", "--env", MODAL_ENV, timeout=60)
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    try:
        apps = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Failed to parse modal app list JSON: {result.stdout}")
    app_names = [app.get("Description", app.get("Name", "")) for app in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in app list. Found: {app_names}"
    )


def test_dict_health_check(deployed_app):
    result = modal_cli(
        "dict", "get", DICT_NAME, "health_check", "--env", MODAL_ENV, timeout=60
    )
    assert result.returncode == 0, (
        f"modal dict get health_check failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    output = result.stdout.strip()
    assert "ok" in output.lower(), (
        f"Expected 'ok' in health_check value, got: {output}"
    )


def test_dict_endpoint_deployed(deployed_app):
    result = modal_cli(
        "dict", "get", DICT_NAME, "endpoint_deployed", "--env", MODAL_ENV, timeout=60
    )
    assert result.returncode == 0, (
        f"modal dict get endpoint_deployed failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    output = result.stdout.strip().lower()
    assert "true" in output or "1" in output, (
        f"Expected truthy value for endpoint_deployed, got: {output}"
    )


def test_source_contains_fastapi(deployed_app):
    with open(APP_FILE, "r") as f:
        source = f.read()
    assert "fastapi" in source.lower(), (
        "app.py does not contain 'fastapi' (case-insensitive)"
    )


def test_source_contains_asgi_app(deployed_app):
    with open(APP_FILE, "r") as f:
        source = f.read()
    assert "asgi_app" in source, "app.py does not contain 'asgi_app'"
