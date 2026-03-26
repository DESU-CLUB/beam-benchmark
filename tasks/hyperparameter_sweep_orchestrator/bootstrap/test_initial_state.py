import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/modal_project"
SWEEP_FILE = "/home/user/modal_project/sweep.py"


def test_python3_available():
    assert shutil.which("python3") is not None, "python3 binary not found in PATH."


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal package not importable: {result.stderr}"


def test_numpy_importable():
    result = subprocess.run(
        ["python3", "-c", "import numpy"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"numpy package not importable: {result.stderr}"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist."


def test_starter_sweep_file_exists():
    assert os.path.isfile(SWEEP_FILE), f"Starter file {SWEEP_FILE} does not exist."


def test_starter_sweep_file_has_modal_app():
    with open(SWEEP_FILE) as f:
        content = f.read()
    assert "modal" in content, f"Expected starter sweep.py to import modal, got: {content[:200]}"
    assert "App" in content or "app" in content, (
        f"Expected starter sweep.py to contain a Modal App stub, got: {content[:200]}"
    )
