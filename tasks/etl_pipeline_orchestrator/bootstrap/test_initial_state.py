import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/modal_project"


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


def test_starter_etl_file_exists():
    etl_file = os.path.join(PROJECT_DIR, "etl.py")
    assert os.path.isfile(etl_file), f"Starter file {etl_file} does not exist."
