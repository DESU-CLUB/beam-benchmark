import os
import subprocess
import pytest
import json
import re

APP_FILE = "/home/user/webhook_processor/app.py"
APP_NAME = "webhook-processor"
MODAL_ENV = "modal-vsdatagen"


def run_modal(args, check=True):
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    result = subprocess.run(
        ["modal"] + args,
        capture_output=True,
        text=True,
        env=env,
    )
    if check:
        assert result.returncode == 0, (
            f"modal {' '.join(args)} failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
    return result


@pytest.fixture(scope="module")
def deployed_app():
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    deploy_result = subprocess.run(
        ["modal", "deploy", APP_FILE],
        capture_output=True,
        text=True,
        env=env,
        cwd="/home/user/webhook_processor",
    )
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nSTDOUT: {deploy_result.stdout}\nSTDERR: {deploy_result.stderr}"
    )
    yield deploy_result
    # Teardown: stop the app
    run_modal(["app", "stop", APP_NAME], check=False)


def test_app_appears_in_app_list(deployed_app):
    result = run_modal(["app", "list", "--json"])
    apps = json.loads(result.stdout)
    app_names = [a.get("Description", "") for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )
