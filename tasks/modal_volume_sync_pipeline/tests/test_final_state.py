import json
import os
import re
import subprocess

import pytest

APP_NAME = "volume-sync-pipeline"
VOLUME_NAME = "data-pipeline-vol"
APP_FILE = "/home/user/volume_pipeline/app.py"
MODAL_ENVIRONMENT = "modal-vsdatagen"


def _modal_env():
    return {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENVIRONMENT}


@pytest.fixture(scope="module")
def deployed_app():
    env = _modal_env()
    result = subprocess.run(
        ["modal", "deploy", APP_FILE, "-e", MODAL_ENVIRONMENT],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, (
        f"modal deploy failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    )
    yield result

    # Teardown: stop the app
    subprocess.run(
        ["modal", "app", "stop", APP_NAME, "-e", MODAL_ENVIRONMENT],
        capture_output=True,
        text=True,
        env=env,
    )


def test_app_appears_in_app_list(deployed_app):
    env = _modal_env()
    result = subprocess.run(
        ["modal", "app", "list", "--json"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"modal app list failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a.get("Description", "") for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_volume_appears_in_volume_list(deployed_app):
    env = _modal_env()
    result = subprocess.run(
        ["modal", "volume", "list", "--json"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"modal volume list failed: {result.stderr}"
    volumes = json.loads(result.stdout)
    volume_names = [v.get("Name", "") for v in volumes]
    assert VOLUME_NAME in volume_names, (
        f"Volume '{VOLUME_NAME}' not found in modal volume list. Found: {volume_names}"
    )
