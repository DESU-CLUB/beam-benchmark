import ast
import json
import os
import shutil
import subprocess

import pytest

PROJECT_DIR = "/home/user/volume_pipeline/"
APP_FILE = "/home/user/volume_pipeline/app.py"


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
    assert os.path.isfile(APP_FILE), f"Starter file {APP_FILE} does not exist"


def _parse_app_file():
    with open(APP_FILE, "r") as f:
        source = f.read()
    return ast.parse(source), source


def test_app_imports_modal():
    tree, source = _parse_app_file()
    imports_modal = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "modal":
                    imports_modal = True
        elif isinstance(node, ast.ImportFrom):
            if node.module == "modal":
                imports_modal = True
    assert imports_modal, "app.py does not import modal"


def test_app_has_modal_app_definition():
    tree, source = _parse_app_file()
    has_app = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(node.value, ast.Call):
                    func = node.value.func
                    if isinstance(func, ast.Attribute):
                        if func.attr == "App" and isinstance(func.value, ast.Name) and func.value.id == "modal":
                            has_app = True
                    elif isinstance(func, ast.Name) and func.id == "App":
                        has_app = True
    assert has_app, "app.py does not define a modal.App instance"


def test_app_has_modal_volume_definition():
    tree, source = _parse_app_file()
    has_volume = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if isinstance(node.value, ast.Call):
                func = node.value.func
                # modal.Volume.from_name(...)
                if (
                    isinstance(func, ast.Attribute)
                    and func.attr == "from_name"
                    and isinstance(func.value, ast.Attribute)
                    and func.value.attr == "Volume"
                ):
                    has_volume = True
                # Volume.from_name(...) after from modal import Volume
                elif isinstance(func, ast.Attribute) and func.attr == "from_name":
                    if isinstance(func.value, ast.Name) and func.value.id == "Volume":
                        has_volume = True
    assert has_volume, "app.py does not define a modal.Volume using from_name"
