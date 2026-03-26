import os
import shutil
import subprocess
import pytest

PROJECT_DIR = "/home/user/event_pipeline"


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


def test_starter_app_file_exists():
    app_file = os.path.join(PROJECT_DIR, "app.py")
    assert os.path.isfile(app_file), f"Starter file {app_file} does not exist."


def test_starter_app_has_modal_import():
    app_file = os.path.join(PROJECT_DIR, "app.py")
    with open(app_file) as f:
        source = f.read()
    assert "import modal" in source, "app.py must contain 'import modal'."


def test_starter_app_has_modal_app():
    app_file = os.path.join(PROJECT_DIR, "app.py")
    with open(app_file) as f:
        source = f.read()
    assert "modal.App" in source, "app.py must contain a modal.App() definition."
