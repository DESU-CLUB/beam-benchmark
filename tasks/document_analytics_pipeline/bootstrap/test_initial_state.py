import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/modal_project"
PIPELINE_FILE = "/home/user/modal_project/pipeline.py"


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


def test_starter_pipeline_file_exists():
    assert os.path.isfile(PIPELINE_FILE), (
        f"Starter file {PIPELINE_FILE} does not exist."
    )


def test_starter_pipeline_has_modal_app():
    with open(PIPELINE_FILE) as f:
        content = f.read()
    assert "modal.App" in content or "modal.App(" in content, (
        f"Starter pipeline.py at {PIPELINE_FILE} does not contain a Modal App stub."
    )
