import ast
import os
import shutil
import subprocess

import pytest

APP_DIR = "/home/user/modal_fastapi"
APP_FILE = "/home/user/modal_fastapi/app.py"


def test_python3_in_path():
    result = shutil.which("python3")
    assert result is not None, "python3 not found in PATH"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal not importable: {result.stderr}"


def test_app_directory_exists():
    assert os.path.isdir(APP_DIR), f"Directory {APP_DIR} does not exist"


def test_app_file_exists():
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
    assert "fastapi-json-transform" in source, (
        "app.py does not contain app name 'fastapi-json-transform'"
    )


def test_no_asgi_app_decorator():
    with open(APP_FILE, "r") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        pytest.skip("app.py has syntax errors, skipping AST check")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                decorator_str = ast.unparse(decorator)
                assert "asgi_app" not in decorator_str, (
                    f"Function '{node.name}' already has an asgi_app decorator"
                )


def test_no_web_endpoint_decorator():
    with open(APP_FILE, "r") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        pytest.skip("app.py has syntax errors, skipping AST check")

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for decorator in node.decorator_list:
                decorator_str = ast.unparse(decorator)
                assert "web_endpoint" not in decorator_str, (
                    f"Function '{node.name}' already has a web_endpoint decorator"
                )
