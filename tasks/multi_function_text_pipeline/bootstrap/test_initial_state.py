import os
import subprocess
import pytest


def test_python3_in_path():
    result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "python3 not found in PATH"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal not importable: {result.stderr}"


def test_modal_pipeline_dir_exists():
    assert os.path.isdir("/home/user/modal_pipeline"), (
        "/home/user/modal_pipeline directory does not exist"
    )


def test_app_py_exists():
    assert os.path.isfile("/home/user/modal_pipeline/app.py"), (
        "/home/user/modal_pipeline/app.py does not exist"
    )


def test_app_py_has_import_modal():
    with open("/home/user/modal_pipeline/app.py", "r") as f:
        source = f.read()
    assert "import modal" in source, "app.py does not contain 'import modal'"


def test_app_py_has_modal_app():
    with open("/home/user/modal_pipeline/app.py", "r") as f:
        source = f.read()
    assert "modal.App" in source, "app.py does not contain 'modal.App'"


def test_app_py_has_app_name():
    with open("/home/user/modal_pipeline/app.py", "r") as f:
        source = f.read()
    assert "text-pipeline" in source, "app.py does not contain app name 'text-pipeline'"


def test_clean_text_not_defined():
    with open("/home/user/modal_pipeline/app.py", "r") as f:
        source = f.read()
    assert "def clean_text" not in source, (
        "clean_text should not be defined yet in starter app.py"
    )


def test_count_words_not_defined():
    with open("/home/user/modal_pipeline/app.py", "r") as f:
        source = f.read()
    assert "def count_words" not in source, (
        "count_words should not be defined yet in starter app.py"
    )


def test_summarize_not_defined():
    with open("/home/user/modal_pipeline/app.py", "r") as f:
        source = f.read()
    assert "def summarize" not in source, (
        "summarize should not be defined yet in starter app.py"
    )
