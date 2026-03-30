import os
import subprocess
import pytest


def test_python3_available():
    result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "python3 is not available"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal; print(modal.__version__)"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal is not importable: {result.stderr}"


def test_project_directory_exists():
    assert os.path.isdir("/home/user/modal_project"), (
        "/home/user/modal_project directory does not exist"
    )


def test_app_file_does_not_exist():
    assert not os.path.exists(
        "/home/user/modal_project/modal_event_pipeline.py"
    ), "App file already exists — it should not exist before the agent creates it"
