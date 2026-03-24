import ast
import os
import shutil
import subprocess

import pytest

APP_FILE = "/home/user/modal_secrets/app.py"
APP_DIR = "/home/user/modal_secrets"


def test_python3_in_path():
    assert shutil.which("python3") is not None, "python3 not found in PATH"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal not importable: {result.stderr}"


def test_modal_secrets_dir_exists():
    assert os.path.isdir(APP_DIR), f"Directory {APP_DIR} does not exist"


def test_app_py_exists():
    assert os.path.isfile(APP_FILE), f"File {APP_FILE} does not exist"


def test_app_py_has_import_modal():
    with open(APP_FILE) as f:
        source = f.read()
    assert "import modal" in source, "app.py does not contain 'import modal'"


def test_app_py_has_import_os():
    with open(APP_FILE) as f:
        source = f.read()
    assert "import os" in source, "app.py does not contain 'import os'"


def test_app_py_has_modal_app():
    with open(APP_FILE) as f:
        source = f.read()
    assert "modal.App" in source, "app.py does not contain 'modal.App'"


def test_app_py_has_secret_api_key_app_name():
    with open(APP_FILE) as f:
        source = f.read()
    assert '"secret-api-key"' in source, (
        'app.py does not contain app name "secret-api-key"'
    )


def test_fetch_with_key_not_defined_yet():
    with open(APP_FILE) as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        pytest.skip("app.py has syntax errors, skipping AST check")
    function_names = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    ]
    assert "fetch_with_key" not in function_names, (
        "fetch_with_key function should not be defined in the initial state"
    )
