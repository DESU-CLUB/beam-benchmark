import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/hp_sweep"
APP_FILE = "/home/user/hp_sweep/app.py"


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
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"App file {APP_FILE} does not exist."


def test_app_file_has_modal_import():
    with open(APP_FILE) as f:
        content = f.read()
    assert "import modal" in content, (
        f"Expected app.py to contain 'import modal', got: {content[:200]}"
    )


def test_app_file_has_modal_app():
    with open(APP_FILE) as f:
        content = f.read()
    assert "modal.App" in content, (
        f"Expected app.py to contain a modal.App(...) stub, got: {content[:200]}"
    )
