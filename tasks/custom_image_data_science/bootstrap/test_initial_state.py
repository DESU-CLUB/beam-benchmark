import ast
import os
import shutil
import subprocess
import pytest


APP_FILE = "/home/user/modal_ds/app.py"
APP_DIR = "/home/user/modal_ds"


def test_python3_in_path():
    assert shutil.which("python3") is not None, "python3 not found in PATH"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal is not importable: {result.stderr}"


def test_app_dir_exists():
    assert os.path.isdir(APP_DIR), f"Expected directory {APP_DIR} does not exist"


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"Expected file {APP_FILE} does not exist"


def test_app_file_has_import_modal():
    with open(APP_FILE, "r") as f:
        source = f.read()
    assert "import modal" in source, "app.py does not contain 'import modal'"


def test_app_file_has_modal_app():
    with open(APP_FILE, "r") as f:
        source = f.read()
    assert "modal.App" in source, "app.py does not contain 'modal.App'"


def test_app_file_has_correct_app_name():
    with open(APP_FILE, "r") as f:
        source = f.read()
    assert "custom-image-data-science" in source, (
        "app.py does not contain app name 'custom-image-data-science'"
    )


def test_run_stats_not_defined_yet():
    with open(APP_FILE, "r") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # File may not be fully valid yet; just check for function name string
        assert "run_stats" not in source, (
            "'run_stats' function already defined in app.py before task started"
        )
        return
    function_names = [
        node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]
    assert "run_stats" not in function_names, (
        "'run_stats' function already defined in app.py before task started"
    )
