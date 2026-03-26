import subprocess
import sys
import os


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


def test_etl_pipeline_directory_exists():
    assert os.path.isdir("/home/user/etl_pipeline"), (
        "/home/user/etl_pipeline directory does not exist"
    )


def test_app_py_exists():
    assert os.path.isfile("/home/user/etl_pipeline/app.py"), (
        "/home/user/etl_pipeline/app.py does not exist"
    )


def test_app_py_has_modal_import():
    with open("/home/user/etl_pipeline/app.py", "r") as f:
        content = f.read()
    assert "import modal" in content, "app.py does not contain 'import modal'"


def test_app_py_has_modal_app():
    with open("/home/user/etl_pipeline/app.py", "r") as f:
        content = f.read()
    assert "modal.App" in content, "app.py does not contain 'modal.App'"
