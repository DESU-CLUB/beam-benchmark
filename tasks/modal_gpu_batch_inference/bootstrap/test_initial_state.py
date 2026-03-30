import subprocess
import sys
import os


def test_python3_available():
    result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "python3 is not available"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal is not importable: {result.stderr}"


def test_project_dir_exists():
    assert os.path.isdir("/home/user/modal_project"), (
        "/home/user/modal_project directory does not exist"
    )


def test_app_file_does_not_exist():
    assert not os.path.exists(
        "/home/user/modal_project/modal_gpu_batch_inference.py"
    ), "App file should not exist before the task is completed"
