import ast
import os
import subprocess
import pytest


APP_DIR = "/home/user/modal_volume_logs"
APP_FILE = "/home/user/modal_volume_logs/app.py"


def test_python3_in_path():
    result = subprocess.run(["python3", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "python3 not found in PATH"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal is not importable: {result.stderr}"


def test_app_dir_exists():
    assert os.path.isdir(APP_DIR), f"Directory {APP_DIR} does not exist"


def test_app_py_exists():
    assert os.path.isfile(APP_FILE), f"File {APP_FILE} does not exist"


def test_app_py_has_import_modal():
    with open(APP_FILE, "r") as f:
        source = f.read()
    assert "import modal" in source, "app.py does not contain 'import modal'"


def test_app_py_has_modal_app():
    with open(APP_FILE, "r") as f:
        source = f.read()
    assert "modal.App" in source, "app.py does not contain 'modal.App'"


def test_app_py_has_app_name():
    with open(APP_FILE, "r") as f:
        source = f.read()
    assert "volume-log-archiver" in source, (
        "app.py does not contain app name 'volume-log-archiver'"
    )


def test_write_logs_function_not_present():
    with open(APP_FILE, "r") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        pytest.skip("app.py has syntax errors, skipping AST check")
    func_names = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert "write_logs" not in func_names, (
        "write_logs function already exists in app.py (should not be pre-defined)"
    )


def test_read_logs_function_not_present():
    with open(APP_FILE, "r") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        pytest.skip("app.py has syntax errors, skipping AST check")
    func_names = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert "read_logs" not in func_names, (
        "read_logs function already exists in app.py (should not be pre-defined)"
    )
