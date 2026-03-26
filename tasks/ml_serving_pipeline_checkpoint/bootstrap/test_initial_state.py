import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/modal_project"
APP_FILE = "/home/user/modal_project/app.py"


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal package not importable: {result.stderr}"


def test_sklearn_importable():
    result = subprocess.run(
        ["python3", "-c", "import sklearn"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"scikit-learn package not importable: {result.stderr}"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_starter_app_file_exists():
    assert os.path.isfile(APP_FILE), f"Starter app file {APP_FILE} does not exist."


def test_starter_app_has_modal_import():
    with open(APP_FILE) as f:
        contents = f.read()
    assert "import modal" in contents, (
        f"Starter {APP_FILE} does not contain 'import modal'. Contents: {contents!r}"
    )
