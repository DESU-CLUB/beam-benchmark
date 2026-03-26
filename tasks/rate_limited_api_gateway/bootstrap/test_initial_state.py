import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/modal_project"
GATEWAY_FILE = "/home/user/modal_project/gateway.py"


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal package not importable: {result.stderr}"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )


def test_gateway_file_exists():
    assert os.path.isfile(GATEWAY_FILE), (
        f"Starter file {GATEWAY_FILE} does not exist."
    )


def test_gateway_file_has_modal_app_stub():
    with open(GATEWAY_FILE, "r") as f:
        contents = f.read()
    assert "import modal" in contents, (
        f"Starter file {GATEWAY_FILE} does not contain 'import modal'."
    )
    assert "modal.App" in contents or "modal.App(" in contents, (
        f"Starter file {GATEWAY_FILE} does not contain a Modal App stub (modal.App)."
    )
