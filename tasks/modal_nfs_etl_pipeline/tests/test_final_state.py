import json
import os
import subprocess

import pytest

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/etl_pipeline/app.py"
APP_NAME = "nfs-etl-pipeline"
NFS_NAME = "etl-shared-fs"
SECRET_NAME = "etl-db-config"
DICT_NAME = "etl-pipeline-state"


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
    # Create secret with DB credentials
    secret_result = modal_cli(
        "secret", "create", SECRET_NAME,
        "DB_HOST=localhost", "DB_PORT=5432",
        "--force",
        timeout=60,
    )
    assert secret_result.returncode == 0, (
        f"Failed to create secret: {secret_result.stderr}"
    )

    # Deploy the app
    deploy_result = modal_cli("deploy", APP_FILE, timeout=300)
    assert deploy_result.returncode == 0, (
        f"Failed to deploy app: {deploy_result.stderr}\n{deploy_result.stdout}"
    )

    # Run the local entrypoint
    run_result = modal_cli("run", APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"Failed to run app: {run_result.stderr}\n{run_result.stdout}"
    )

    yield {
        "deploy": deploy_result,
        "run": run_result,
    }

    # Teardown: stop the app
    modal_cli("app", "stop", APP_NAME, timeout=60)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"{APP_FILE} does not exist"


def test_deploy_succeeds(deployed_app):
    assert deployed_app["deploy"].returncode == 0


def test_app_in_app_list(deployed_app):
    result = modal_cli("app", "list", "--json", timeout=60)
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_descriptions = [a.get("Description", "") for a in apps]
    assert any(APP_NAME in desc for desc in app_descriptions), (
        f"App '{APP_NAME}' not found in app list. Apps: {app_descriptions}"
    )


def test_secret_in_secret_list(deployed_app):
    result = modal_cli("secret", "list", "--json", timeout=60)
    assert result.returncode == 0, f"modal secret list failed: {result.stderr}"
    secrets = json.loads(result.stdout)
    secret_names = [s.get("Name", "") for s in secrets]
    assert any(SECRET_NAME in name for name in secret_names), (
        f"Secret '{SECRET_NAME}' not found in secret list. Secrets: {secret_names}"
    )


def test_dict_last_run_status(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "last_run_status", timeout=60)
    assert result.returncode == 0, (
        f"modal dict get last_run_status failed: {result.stderr}\n{result.stdout}"
    )
    assert "success" in result.stdout, (
        f"Expected 'success' in dict output, got: {result.stdout}"
    )


def test_dict_batches_processed(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "batches_processed", timeout=60)
    assert result.returncode == 0, (
        f"modal dict get batches_processed failed: {result.stderr}\n{result.stdout}"
    )
    assert "2" in result.stdout, (
        f"Expected '2' in dict output, got: {result.stdout}"
    )
