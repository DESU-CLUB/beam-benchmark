import os
import subprocess
import pytest
import json
import re

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_pipeline/app.py"
APP_NAME = "text-pipeline"
DICT_NAME = "text-pipeline-output"


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
    # Deploy the app
    deploy_result = modal_cli("deploy", "--env", MODAL_ENV, APP_FILE, timeout=300)
    assert deploy_result.returncode == 0, (
        f"Deploy failed:\nSTDOUT: {deploy_result.stdout}\nSTDERR: {deploy_result.stderr}"
    )

    # Run the local entrypoint
    run_result = modal_cli("run", "--env", MODAL_ENV, APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"Run failed:\nSTDOUT: {run_result.stdout}\nSTDERR: {run_result.stderr}"
    )

    yield {
        "deploy": deploy_result,
        "run": run_result,
    }

    # Teardown: stop the app
    modal_cli("app", "stop", APP_NAME, "--env", MODAL_ENV, timeout=120)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"{APP_FILE} does not exist"


def test_deploy_succeeds(deployed_app):
    assert deployed_app["deploy"].returncode == 0, "Deploy did not succeed"


def test_app_in_app_list(deployed_app):
    result = modal_cli("app", "list", "--json", "--env", MODAL_ENV, timeout=60)
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    try:
        apps = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Could not parse modal app list JSON: {result.stdout}")
    app_names = [a.get("Description", a.get("Name", a.get("name", ""))) for a in apps]
    assert any(APP_NAME in name for name in app_names), (
        f"App '{APP_NAME}' not found in app list: {app_names}"
    )


def test_dict_summary_non_empty(deployed_app):
    result = modal_cli(
        "dict", "get", DICT_NAME, "summary", "--env", MODAL_ENV, timeout=60
    )
    assert result.returncode == 0, (
        f"modal dict get summary failed:\n{result.stdout}\n{result.stderr}"
    )
    output = result.stdout.strip()
    assert output, "Dict key 'summary' is empty"


def test_dict_pipeline_stages(deployed_app):
    result = modal_cli(
        "dict", "get", DICT_NAME, "pipeline_stages", "--env", MODAL_ENV, timeout=60
    )
    assert result.returncode == 0, (
        f"modal dict get pipeline_stages failed:\n{result.stdout}\n{result.stderr}"
    )
    output = result.stdout.strip()
    assert output in ("3", 3, "3\n"), (
        f"Expected pipeline_stages to be 3, got: {output!r}"
    )


def test_three_functions_defined():
    with open(APP_FILE, "r") as f:
        source = f.read()
    decorator_count = len(re.findall(r"@app\.function", source))
    assert decorator_count >= 3, (
        f"Expected at least 3 @app.function decorators, found {decorator_count}"
    )
    assert "def clean_text" in source, "clean_text function not found in app.py"
    assert "def count_words" in source, "count_words function not found in app.py"
    assert "def summarize" in source, "summarize function not found in app.py"
