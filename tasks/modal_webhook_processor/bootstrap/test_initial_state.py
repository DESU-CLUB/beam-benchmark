import os
import shutil
import subprocess
import pytest
import ast
import json

PROJECT_DIR = "/home/user/webhook_processor"
APP_FILE = "/home/user/webhook_processor/app.py"


def test_python3_in_path():
    assert shutil.which("python3") is not None, "python3 not found in PATH"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal package not importable: {result.stderr}"


def test_project_directory_exists():
    assert os.path.isdir(PROJECT_DIR), f"Project directory {PROJECT_DIR} does not exist"


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"Starter app.py not found at {APP_FILE}"


def test_app_file_imports_modal():
    with open(APP_FILE, "r") as f:
        source = f.read()
    tree = ast.parse(source)
    imports = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    modal_imported = any(
        (isinstance(node, ast.Import) and any(alias.name == "modal" for alias in node.names))
        or (isinstance(node, ast.ImportFrom) and node.module == "modal")
        for node in imports
    )
    assert modal_imported, "app.py does not import modal"


def test_app_file_defines_modal_app():
    with open(APP_FILE, "r") as f:
        source = f.read()
    tree = ast.parse(source)
    # Look for an assignment where the value is a call to modal.App(...)
    found_app = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call):
                func = node.value.func
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr == "App"
                    and isinstance(func.value, ast.Name)
                    and func.value.id == "modal"
                ):
                    found_app = True
                    break
                elif isinstance(func, ast.Name) and func.id == "App":
                    found_app = True
                    break
    assert found_app, "app.py does not define a modal.App instance"
